import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


def calculate_match_score(user_preferences, story_features):
    """
    Calculate match score between user preferences and story features
    In a real application, this would use more sophisticated algorithms
    """
    # Simple cosine similarity for demonstration
    user_vector = np.array([p.weight for p in user_preferences])
    story_vector = np.array(
        [1 if f in story_features else 0 for f in user_preferences])

    if len(user_vector) == 0 or len(story_vector) == 0:
        return 0

    similarity = cosine_similarity([user_vector], [story_vector])[0][0]
    return int(similarity * 100)


def update_user_preferences(user_id, story_id, is_positive):
    """
    Update user preferences based on feedback
    """
    # In a real application, this would:
    # 1. Get the story's features
    # 2. Update the user's preference weights
    # 3. Store the updated preferences
    pass
