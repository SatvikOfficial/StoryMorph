from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from models import db, Story, User, UserInteraction
from ai_model import StoryRecommender
import os

app = Flask(__name__, static_folder='static')
# Allow CORS from all origins
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///storymorph.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
recommender = StoryRecommender()

# Create database tables
with app.app_context():
    db.create_all()


@app.route('/')
def index():
    return send_from_directory('docs', 'index.html')


@app.route('/api/users')
def get_users():
    # Fixed set of 4 users
    users = [
        {'id': 1, 'username': 'Alex', 'preferences': {'Fiction': 'high', 'Self-Help': 'medium',
                                                      'Mystery': 'low', 'Romance': 'medium', 'History': 'low', 'Business': 'high'}},
        {'id': 2, 'username': 'Taylor', 'preferences': {'Fiction': 'medium', 'Self-Help': 'high',
                                                        'Mystery': 'medium', 'Romance': 'high', 'History': 'medium', 'Business': 'low'}},
        {'id': 3, 'username': 'Jordan', 'preferences': {'Fiction': 'low', 'Self-Help': 'high',
                                                        'Mystery': 'high', 'Romance': 'low', 'History': 'high', 'Business': 'medium'}},
        {'id': 4, 'username': 'Morgan', 'preferences': {'Fiction': 'high', 'Self-Help': 'low',
                                                        'Mystery': 'medium', 'Romance': 'high', 'History': 'medium', 'Business': 'high'}}
    ]
    return jsonify(users)


@app.route('/api/recommendations', methods=['GET', 'POST'])
def get_recommendations():
    if request.method == 'POST':
        data = request.json
        user_id = data.get('user_id')
        preferences = data.get('preferences', {})
        category = data.get('category', 'All')
        recommendation_type = data.get('type', 'all')
    else:
        user_id = request.args.get('user_id')
        preferences = {}
        category = request.args.get('category', 'All')
        recommendation_type = request.args.get('type', 'all')

    if not user_id:
        return jsonify({'stories': []})

    try:
        # Sample stories for testing
        sample_stories = [
            {
                'id': 1,
                'title': 'The Silent Patient',
                'author': 'Alex Michaelides',
                'category': 'Mystery',
                'match_score': 98,
                'cover_image': '/static/placeholder.jpg'
            },
            {
                'id': 2,
                'title': 'Atomic Habits',
                'author': 'James Clear',
                'category': 'Self-Help',
                'match_score': 95,
                'cover_image': '/static/placeholder.jpg'
            },
            {
                'id': 3,
                'title': 'Project Hail Mary',
                'author': 'Andy Weir',
                'category': 'Fiction',
                'match_score': 94,
                'cover_image': '/static/placeholder.jpg'
            },
            {
                'id': 4,
                'title': 'The Midnight Library',
                'author': 'Matt Haig',
                'category': 'Fiction',
                'match_score': 92,
                'cover_image': '/static/placeholder.jpg'
            },
            {
                'id': 5,
                'title': 'Where the Crawdads Sing',
                'author': 'Delia Owens',
                'category': 'Fiction',
                'match_score': 90,
                'cover_image': '/static/placeholder.jpg'
            },
            {
                'id': 6,
                'title': 'Educated',
                'author': 'Tara Westover',
                'category': 'History',
                'match_score': 88,
                'cover_image': '/static/placeholder.jpg'
            },
            {
                'id': 7,
                'title': 'The Alchemist',
                'author': 'Paulo Coelho',
                'category': 'Fiction',
                'match_score': 85,
                'cover_image': '/static/placeholder.jpg'
            },
            {
                'id': 8,
                'title': 'The Four Agreements',
                'author': 'Don Miguel Ruiz',
                'category': 'Self-Help',
                'match_score': 82,
                'cover_image': '/static/placeholder.jpg'
            },
            {
                'id': 9,
                'title': 'The Power of Now',
                'author': 'Eckhart Tolle',
                'category': 'Self-Help',
                'match_score': 80,
                'cover_image': '/static/placeholder.jpg'
            },
            {
                'id': 10,
                'title': 'The 7 Habits of Highly Effective People',
                'author': 'Stephen R. Covey',
                'category': 'Business',
                'match_score': 78,
                'cover_image': '/static/placeholder.jpg'
            },
            {
                'id': 11,
                'title': 'The Art of War',
                'author': 'Sun Tzu',
                'category': 'Business',
                'match_score': 75,
                'cover_image': '/static/placeholder.jpg'
            },
            {
                'id': 12,
                'title': 'The Lean Startup',
                'author': 'Eric Ries',
                'category': 'Business',
                'match_score': 72,
                'cover_image': '/static/placeholder.jpg'
            },
            {
                'id': 13,
                'title': 'The Psychology of Money',
                'author': 'Morgan Housel',
                'category': 'Business',
                'match_score': 70,
                'cover_image': '/static/placeholder.jpg'
            },
            {
                'id': 14,
                'title': 'The Subtle Art of Not Giving a F*ck',
                'author': 'Mark Manson',
                'category': 'Self-Help',
                'match_score': 68,
                'cover_image': '/static/placeholder.jpg'
            },
            {
                'id': 15,
                'title': 'The 48 Laws of Power',
                'author': 'Robert Greene',
                'category': 'Business',
                'match_score': 65,
                'cover_image': '/static/placeholder.jpg'
            },
            {
                'id': 16,
                'title': 'The 5 Love Languages',
                'author': 'Gary Chapman',
                'category': 'Romance',
                'match_score': 62,
                'cover_image': '/static/placeholder.jpg'
            },
            {
                'id': 17,
                'title': 'The Road Less Traveled',
                'author': 'M. Scott Peck',
                'category': 'Self-Help',
                'match_score': 60,
                'cover_image': '/static/placeholder.jpg'
            },
            {
                'id': 18,
                'title': 'The Four Winds',
                'author': 'Kristin Hannah',
                'category': 'Fiction',
                'match_score': 58,
                'cover_image': '/static/placeholder.jpg'
            }
        ]

        # Filter by category if specified
        if category != 'All':
            sample_stories = [
                s for s in sample_stories if s['category'] == category]

        # Return all recommendations
        return jsonify({
            'highly_recommended': sample_stories[:6],
            'because_you_listened': sample_stories[6:12],
            'new_discoveries': sample_stories[12:18]
        })

    except Exception as e:
        print(f"Error getting recommendations: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/feedback', methods=['POST'])
def handle_feedback():
    data = request.json
    user_id = data.get('user_id')
    story_id = data.get('story_id')
    is_positive = data.get('is_positive')
    section = data.get('section')

    if not all([user_id, story_id, is_positive is not None]):
        return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400

    try:
        recommender.process_feedback(user_id, story_id, is_positive, section)
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/users/<int:user_id>')
def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    return jsonify({
        'id': user.id,
        'username': user.username,
        'preferences': user.preferences
    })


@app.route('/api/users/<int:user_id>/preferences', methods=['PUT'])
def update_user_preferences(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.json
    preferences = data.get('preferences')

    if not preferences:
        return jsonify({'error': 'Preferences data is required'}), 400

    try:
        user.preferences = preferences
        db.session.commit()
        return jsonify({'status': 'success'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/preferences', methods=['POST'])
def update_preferences():
    try:
        data = request.json
        user_id = data.get('user_id')
        preferences = data.get('preferences', {})

        if not user_id:
            return jsonify({'error': 'User ID is required'}), 400

        # In a real app, we would update the database here
        # For now, we'll just return success
        return jsonify({
            'status': 'success',
            'message': 'Preferences updated successfully'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
