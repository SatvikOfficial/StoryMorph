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
        recommendation_type = data.get('type', 'highly_recommended')
    else:
        user_id = request.args.get('user_id')
        preferences = {}
        category = request.args.get('category', 'All')
        recommendation_type = request.args.get('type', 'highly_recommended')

    if not user_id:
        return jsonify({'stories': []})

    try:
        # Get recommendations from the AI model
        recommendations = recommender.get_recommendations(
            user_id=user_id,
            category=category,
            recommendation_type=recommendation_type
        )

        # Add placeholder image URL to each story
        for story in recommendations:
            story['cover_image'] = 'file:///C:/Users/Lenovo/StoryMorph/placeholder.jpg'

        return jsonify({
            'highly_recommended': recommendations[:6],
            'because_you_listened': recommendations[6:12],
            'new_discoveries': recommendations[12:18]
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


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
