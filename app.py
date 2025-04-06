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


@app.route('/api/recommendations')
def get_recommendations():
    category = request.args.get('category', 'All')
    recommendation_type = request.args.get('type', 'highly_recommended')
    user_id = request.args.get('user_id')

    if not user_id:
        return jsonify({'stories': []})

    # Fixed set of stories
    stories = [
        # Fiction
        {'id': 1, 'title': 'The Silent Patient', 'author': 'Alex Michaelides',
            'category': 'Fiction', 'match_score': 98},
        {'id': 2, 'title': 'Project Hail Mary', 'author': 'Andy Weir',
            'category': 'Fiction', 'match_score': 95},
        {'id': 3, 'title': 'The Midnight Library', 'author': 'Matt Haig',
            'category': 'Fiction', 'match_score': 94},
        {'id': 4, 'title': 'Where the Crawdads Sing', 'author': 'Delia Owens',
            'category': 'Fiction', 'match_score': 92},
        {'id': 5, 'title': 'The Vanishing Half', 'author': 'Brit Bennett',
            'category': 'Fiction', 'match_score': 90},
        {'id': 6, 'title': 'The House in the Cerulean Sea',
            'author': 'TJ Klune', 'category': 'Fiction', 'match_score': 88},
        {'id': 7, 'title': 'The Invisible Life of Addie LaRue',
            'author': 'V.E. Schwab', 'category': 'Fiction', 'match_score': 86},
        {'id': 8, 'title': 'The Four Winds', 'author': 'Kristin Hannah',
            'category': 'Fiction', 'match_score': 84},

        # Self-Help
        {'id': 9, 'title': 'Atomic Habits', 'author': 'James Clear',
            'category': 'Self-Help', 'match_score': 97},
        {'id': 10, 'title': 'The Power of Now', 'author': 'Eckhart Tolle',
            'category': 'Self-Help', 'match_score': 95},
        {'id': 11, 'title': 'The 7 Habits of Highly Effective People',
            'author': 'Stephen Covey', 'category': 'Self-Help', 'match_score': 93},
        {'id': 12, 'title': 'The Subtle Art of Not Giving a F*ck',
            'author': 'Mark Manson', 'category': 'Self-Help', 'match_score': 91},
        {'id': 13, 'title': 'The 5 AM Club', 'author': 'Robin Sharma',
            'category': 'Self-Help', 'match_score': 89},
        {'id': 14, 'title': 'The Four Agreements', 'author': 'Don Miguel Ruiz',
            'category': 'Self-Help', 'match_score': 87},
        {'id': 15, 'title': 'The Monk Who Sold His Ferrari',
            'author': 'Robin Sharma', 'category': 'Self-Help', 'match_score': 85},
        {'id': 16, 'title': 'Ikigai: The Japanese Secret',
            'author': 'Héctor García', 'category': 'Self-Help', 'match_score': 83},

        # Mystery
        {'id': 17, 'title': 'The Guest List', 'author': 'Lucy Foley',
            'category': 'Mystery', 'match_score': 96},
        {'id': 18, 'title': 'The Sanatorium', 'author': 'Sarah Pearse',
            'category': 'Mystery', 'match_score': 94},
        {'id': 19, 'title': 'The Push', 'author': 'Ashley Audrain',
            'category': 'Mystery', 'match_score': 92},
        {'id': 20, 'title': 'The Maid', 'author': 'Nita Prose',
            'category': 'Mystery', 'match_score': 90},
        {'id': 21, 'title': 'The Thursday Murder Club',
            'author': 'Richard Osman', 'category': 'Mystery', 'match_score': 88},
        {'id': 22, 'title': 'The Paris Apartment', 'author': 'Lucy Foley',
            'category': 'Mystery', 'match_score': 86},
        {'id': 23, 'title': 'The Last Thing He Told Me',
            'author': 'Laura Dave', 'category': 'Mystery', 'match_score': 84},
        {'id': 24, 'title': 'The Night She Disappeared',
            'author': 'Lisa Jewell', 'category': 'Mystery', 'match_score': 82},

        # Romance
        {'id': 25, 'title': 'The Love Hypothesis', 'author': 'Ali Hazelwood',
            'category': 'Romance', 'match_score': 95},
        {'id': 26, 'title': 'It Ends with Us', 'author': 'Colleen Hoover',
            'category': 'Romance', 'match_score': 93},
        {'id': 27, 'title': 'The Spanish Love Deception',
            'author': 'Elena Armas', 'category': 'Romance', 'match_score': 91},
        {'id': 28, 'title': 'People We Meet on Vacation',
            'author': 'Emily Henry', 'category': 'Romance', 'match_score': 89},
        {'id': 29, 'title': 'The Hating Game', 'author': 'Sally Thorne',
            'category': 'Romance', 'match_score': 87},
        {'id': 30, 'title': 'Beach Read', 'author': 'Emily Henry',
            'category': 'Romance', 'match_score': 85},
        {'id': 31, 'title': 'Red, White & Royal Blue',
            'author': 'Casey McQuiston', 'category': 'Romance', 'match_score': 83},
        {'id': 32, 'title': 'The Kiss Quotient', 'author': 'Helen Hoang',
            'category': 'Romance', 'match_score': 81},

        # History
        {'id': 33, 'title': 'Sapiens', 'author': 'Yuval Noah Harari',
            'category': 'History', 'match_score': 96},
        {'id': 34, 'title': 'The Splendid and the Vile',
            'author': 'Erik Larson', 'category': 'History', 'match_score': 94},
        {'id': 35, 'title': 'The Warmth of Other Suns',
            'author': 'Isabel Wilkerson', 'category': 'History', 'match_score': 92},
        {'id': 36, 'title': 'The Code Breaker', 'author': 'Walter Isaacson',
            'category': 'History', 'match_score': 90},
        {'id': 37, 'title': 'The Bomber Mafia', 'author': 'Malcolm Gladwell',
            'category': 'History', 'match_score': 88},
        {'id': 38, 'title': 'The Splendid and the Vile',
            'author': 'Erik Larson', 'category': 'History', 'match_score': 86},
        {'id': 39, 'title': 'The Splendid and the Vile',
            'author': 'Erik Larson', 'category': 'History', 'match_score': 84},
        {'id': 40, 'title': 'The Splendid and the Vile',
            'author': 'Erik Larson', 'category': 'History', 'match_score': 82},

        # Business
        {'id': 41, 'title': 'Atomic Habits', 'author': 'James Clear',
            'category': 'Business', 'match_score': 97},
        {'id': 42, 'title': 'The Psychology of Money',
            'author': 'Morgan Housel', 'category': 'Business', 'match_score': 95},
        {'id': 43, 'title': 'The Lean Startup', 'author': 'Eric Ries',
            'category': 'Business', 'match_score': 93},
        {'id': 44, 'title': 'Good to Great', 'author': 'Jim Collins',
            'category': 'Business', 'match_score': 91},
        {'id': 45, 'title': 'The 48 Laws of Power', 'author': 'Robert Greene',
            'category': 'Business', 'match_score': 89},
        {'id': 46, 'title': 'The Art of War', 'author': 'Sun Tzu',
            'category': 'Business', 'match_score': 87},
        {'id': 47, 'title': 'The 7 Habits of Highly Effective People',
            'author': 'Stephen Covey', 'category': 'Business', 'match_score': 85},
        {'id': 48, 'title': 'The 5 AM Club', 'author': 'Robin Sharma',
            'category': 'Business', 'match_score': 83}
    ]

    # Filter by category if specified
    if category != 'All':
        stories = [s for s in stories if s['category'] == category]

    # Add placeholder image URL to each story
    for story in stories:
        story['cover_image'] = 'file:///C:/Users/Lenovo/StoryMorph/placeholder.jpg'

    # Return different number of recommendations based on type
    if recommendation_type == 'highly_recommended':
        return jsonify({'stories': stories[:6]})  # Top 6 highly recommended
    elif recommendation_type == 'because_you_listened':
        return jsonify({'stories': stories[6:12]})  # Next 6 recommendations
    else:  # new_discoveries
        return jsonify({'stories': stories[12:18]})  # Next 6 recommendations


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
