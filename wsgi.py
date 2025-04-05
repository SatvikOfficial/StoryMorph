from app import app as application
import sys

# Add your project directory to the Python path
path = '/home/your_username/StoryMorph'
if path not in sys.path:
    sys.path.append(path)

# Import your Flask app
