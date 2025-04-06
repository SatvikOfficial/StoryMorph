import random
from datetime import datetime, timedelta
from models import db, User, Story, UserInteraction
from app import app

# Sample data
categories = ['Fiction', 'Self-Help',
              'Mystery', 'Romance', 'History', 'Business']
authors = ['John Smith', 'Jane Doe', 'Robert Johnson',
           'Emily Davis', 'Michael Brown', 'Sarah Wilson']
story_titles = [
    'The Silent Patient', 'Atomic Habits', 'Project Hail Mary', 'The Midnight Library',
    'Where the Crawdads Sing', 'Educated', 'The Alchemist', 'The Four Agreements',
    'The Power of Now', 'The 7 Habits of Highly Effective People', 'The Art of War',
    'The Lean Startup', 'The Psychology of Money', 'The Subtle Art of Not Giving a F*ck',
    'The 48 Laws of Power', 'The 5 Love Languages', 'The Road Less Traveled',
    'The Four Winds', 'The Vanishing Half', 'The Invisible Life of Addie LaRue',
    'The House in the Cerulean Sea', 'The Midnight Library', 'The Guest List',
    'The Push', 'The Sanatorium'
]
user_names = [
    'Alex', 'Taylor', 'Jordan', 'Morgan', 'Casey', 'Riley', 'Jamie', 'Quinn',
    'Avery', 'Peyton', 'Dakota', 'Skyler', 'Rowan', 'Sage', 'Emerson', 'Finley',
    'River', 'Phoenix', 'Blake', 'Cameron'
]


def generate_sample_data():
    with app.app_context():
        # Clear existing data
        UserInteraction.query.delete()
        Story.query.delete()
        User.query.delete()
        db.session.commit()

        # Create users
        users = []
        for name in user_names:
            # Generate random preferences using low/medium/high
            preferences = {}
            for category in categories:
                rand = random.random()
                if rand < 0.33:
                    preferences[category] = 'low'
                elif rand < 0.66:
                    preferences[category] = 'medium'
                else:
                    preferences[category] = 'high'

            user = User(
                username=name,
                email=f"{name.lower()}@example.com",
                preferences=preferences
            )
            users.append(user)
            db.session.add(user)
        db.session.commit()

        # Create stories
        stories = []
        for title in story_titles:
            story = Story(
                title=title,
                author=random.choice(authors),
                category=random.choice(categories),
                description=f"This is a sample description for {title}. It's a {random.choice(categories)} story by {random.choice(authors)}.",
                created_at=datetime.utcnow() - timedelta(days=random.randint(0, 365))
            )
            stories.append(story)
            db.session.add(story)
        db.session.commit()

        # Create user interactions
        for user in users:
            # Each user interacts with 5-15 random stories
            num_interactions = random.randint(5, 15)
            interacted_stories = random.sample(stories, num_interactions)

            for story in interacted_stories:
                # 70% chance of positive interaction
                is_positive = random.random() < 0.7
                interaction = UserInteraction(
                    user_id=user.id,
                    story_id=story.id,
                    is_positive=is_positive,
                    interaction_type='feedback',
                    created_at=datetime.utcnow() - timedelta(days=random.randint(0, 30))
                )
                db.session.add(interaction)

        db.session.commit()
        print(
            f"Generated {len(users)} users, {len(stories)} stories, and {UserInteraction.query.count()} interactions")


if __name__ == '__main__':
    generate_sample_data()
