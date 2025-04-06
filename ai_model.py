import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict
from models import Story, User, UserInteraction, db
from datetime import datetime, timedelta
from flask import current_app


class StoryRecommender:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.story_vectors = None
        self.story_ids = None
        self.user_preferences = {}
        self.last_update = None
        self.update_model()

    def update_model(self):
        """Update the model with all stories from the database"""
        if not current_app:
            return

        stories = Story.query.all()
        if not stories:
            self.story_vectors = None
            self.story_ids = []
            return

        # Prepare story data for vectorization
        story_data = []
        self.story_ids = []
        for story in stories:
            story_data.append(f"{story.title} {story.description}")
            self.story_ids.append(story.id)

        # Vectorize stories
        self.story_vectors = self.vectorizer.fit_transform(story_data)
        self.last_update = datetime.now()

    def get_recommendations(self, user_id, category='All', recommendation_type='highly_recommended'):
        """Get story recommendations for a user"""
        if not current_app:
            return []

        # Update model if needed
        if self.story_vectors is None or not self.story_ids:
            self.update_model()
            if self.story_vectors is None or not self.story_ids:
                return []

        # Get user preferences and recent interactions
        user = User.query.get(user_id)
        if not user:
            return []

        # Get all stories
        stories = Story.query.all()
        if not stories:
            return []

        # Filter by category if specified
        if category != 'All':
            stories = [s for s in stories if s.category == category]

        # Calculate match scores for each story
        recommendations = []
        for story in stories:
            match_score = self._calculate_match_score(user, story)

            # Format the recommendation
            recommendation = {
                'id': story.id,
                'title': story.title,
                'author': story.author,
                'category': story.category,
                'description': story.description,
                'match_score': self._get_preference_level(match_score),
                'cover_image': 'https://picsum.photos/300/400'  # Use consistent placeholder image
            }
            recommendations.append(recommendation)

        # Sort by match score
        recommendations.sort(key=lambda x: self._get_score_value(
            x['match_score']), reverse=True)

        # Return different number of recommendations based on type
        if recommendation_type == 'highly_recommended':
            return recommendations[:6]  # Top 6 highly recommended
        elif recommendation_type == 'because_you_listened':
            return recommendations[6:12]  # Next 6 recommendations
        else:  # new_discoveries
            return recommendations[12:18]  # Next 6 recommendations

    def _get_preference_level(self, score):
        """Convert numerical score to preference level"""
        if score >= 0.7:
            return 'high'
        elif score >= 0.4:
            return 'medium'
        else:
            return 'low'

    def _get_score_value(self, level):
        """Convert preference level to numerical value for sorting"""
        return {'high': 3, 'medium': 2, 'low': 1}.get(level, 0)

    def _calculate_match_score(self, user, story):
        """Calculate match score between user and story"""
        if not current_app:
            return 0.0

        score = 0.0

        # Category preference (40% weight)
        if story.category in user.preferences:
            preference = user.preferences[story.category]
            if preference == 'high':
                score += 0.4
            elif preference == 'medium':
                score += 0.2
            elif preference == 'low':
                score += 0.1

        # Recent interactions (30% weight)
        recent_interactions = UserInteraction.query.filter(
            UserInteraction.user_id == user.id,
            UserInteraction.story_id == story.id,
            UserInteraction.created_at >= datetime.utcnow() - timedelta(days=30)
        ).all()

        if recent_interactions:
            positive_interactions = sum(
                1 for i in recent_interactions if i.is_positive)
            score += 0.3 * (positive_interactions / len(recent_interactions))

        # Author preference (20% weight)
        author_stories = Story.query.filter_by(author=story.author).all()
        if author_stories:
            author_interactions = UserInteraction.query.filter(
                UserInteraction.user_id == user.id,
                UserInteraction.story_id.in_([s.id for s in author_stories])
            ).all()
            if author_interactions:
                positive_author = sum(
                    1 for i in author_interactions if i.is_positive)
                score += 0.2 * (positive_author / len(author_interactions))

        # Content similarity (10% weight)
        if self.story_vectors is not None and story.id in self.story_ids:
            story_idx = self.story_ids.index(story.id)
            story_vector = self.story_vectors[story_idx]

            # Get user's liked stories
            liked_stories = UserInteraction.query.filter_by(
                user_id=user.id,
                is_positive=True
            ).all()

            if liked_stories:
                liked_story_ids = [i.story_id for i in liked_stories]
                liked_indices = [self.story_ids.index(
                    sid) for sid in liked_story_ids if sid in self.story_ids]
                if liked_indices:
                    liked_vectors = self.story_vectors[liked_indices]
                    similarities = cosine_similarity(
                        story_vector, liked_vectors)
                    score += 0.1 * np.mean(similarities)

        return min(score, 1.0)  # Ensure score is between 0 and 1

    def process_feedback(self, user_id, story_id, is_positive, section):
        """Process user feedback and update preferences"""
        if not current_app:
            return

        # Get or create user interaction
        interaction = UserInteraction.query.filter_by(
            user_id=user_id,
            story_id=story_id
        ).first()

        if not interaction:
            interaction = UserInteraction(
                user_id=user_id,
                story_id=story_id,
                is_positive=is_positive,
                interaction_type='feedback'
            )
            db.session.add(interaction)
        else:
            interaction.is_positive = is_positive
            interaction.created_at = datetime.utcnow()

        # Update user preferences
        user = User.query.get(user_id)
        story = Story.query.get(story_id)

        if user and story:
            if story.category not in user.preferences:
                # Initial preference
                user.preferences[story.category] = 'medium'

            # Update preference based on feedback
            if is_positive:
                current_pref = user.preferences[story.category]
                if current_pref == 'low':
                    user.preferences[story.category] = 'medium'
                elif current_pref == 'medium':
                    user.preferences[story.category] = 'high'
            else:
                current_pref = user.preferences[story.category]
                if current_pref == 'high':
                    user.preferences[story.category] = 'medium'
                elif current_pref == 'medium':
                    user.preferences[story.category] = 'low'

        db.session.commit()

        # Update the model periodically
        if not self.last_update or (datetime.now() - self.last_update).days >= 1:
            self.update_model()
