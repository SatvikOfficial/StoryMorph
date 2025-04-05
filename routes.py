from flask import jsonify, request
from app import app, db
from models import Story, User, UserPreference, Feedback
from utils import calculate_match_score
import random

# Sample data for demonstration
SAMPLE_STORIES = [
    {
        'id': 1,
        'title': 'The Silent Patient',
        'author': 'Alex Michaelides',
        'category': 'Mystery',
        'match_score': 98
    },
    {
        'id': 2,
        'title': 'Atomic Habits',
        'author': 'James Clear',
        'category': 'Self-Help',
        'match_score': 95
    },
    {
        'id': 3,
        'title': 'Project Hail Mary',
        'author': 'Andy Weir',
        'category': 'Science Fiction',
        'match_score': 94
    }
]


@app.route('/api/recommendations')
def get_recommendations():
    category = request.args.get('category', 'All')

    if category == 'All':
        stories = SAMPLE_STORIES
    else:
        stories = [s for s in SAMPLE_STORIES if s['category'] == category]

    return jsonify({
        'stories': stories,
        'category': category
    })


@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    data = request.json
    story_id = data.get('story_id')
    is_positive = data.get('is_positive')

    # In a real application, you would:
    # 1. Get the current user from session
    # 2. Create a new Feedback record
    # 3. Update user preferences based on feedback

    return jsonify({
        'status': 'success',
        'message': 'Feedback recorded'
    })


@app.route('/api/categories')
def get_categories():
    categories = ['All', 'Fiction', 'Self-Help',
                  'Mystery', 'Romance', 'History', 'Business']
    return jsonify(categories)
