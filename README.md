# StoryMorph - AI-Powered Story Recommendation System

StoryMorph is an intelligent story recommendation system that uses AI to suggest personalized stories based on user preferences and interactions. It's designed to provide a seamless and engaging experience for discovering new stories.

## Features

- **Personalized Recommendations**: Get story suggestions tailored to your preferences
- **Multiple Recommendation Types**:
  - Highly Recommended: Based on your overall preferences
  - Because You Listened: Similar to your recent interactions
  - New Discoveries: Fresh content in your preferred categories
- **User Preference Customization**: Fine-tune your interests in different story categories
- **Real-time Feedback System**: Like/dislike stories to improve recommendations
- **Category-based Filtering**: Browse stories by category
- **Match Score**: See how well each story matches your preferences

## Tech Stack

- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Python, Flask
- **Database**: SQLite
- **AI/ML**: scikit-learn, TF-IDF Vectorization
- **Deployment**: GitHub Pages (Frontend), Render (Backend)

## Live Demo

[View the live demo](https://yourusername.github.io/StoryMorph/)

## Local Development Setup

1. **Clone the repository**:

   ```bash
   git clone https://github.com/yourusername/StoryMorph.git
   cd StoryMorph
   ```

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize the database**:

   ```bash
   python sample_data.py
   ```

4. **Start the Flask server**:

   ```bash
   python app.py
   ```

5. **Access the application**:
   - Frontend: Open `docs/index.html` in your browser
   - Backend: The API will be available at `http://localhost:5000`

## Project Structure

```
StoryMorph/
├── docs/                    # GitHub Pages directory
│   └── index.html       # Frontend application
├── app.py                  # Flask application
├── models.py              # Database models
├── ai_model.py            # Recommendation engine
├── sample_data.py         # Sample data generator
├── requirements.txt       # Python dependencies
├── Procfile              # Deployment configuration
└── README.md             # Project documentation
```

## API Endpoints

- `GET /api/users` - Get all users
- `GET /api/users/<user_id>` - Get specific user
- `PUT /api/users/<user_id>/preferences` - Update user preferences
- `GET /api/recommendations` - Get story recommendations
- `POST /api/feedback` - Submit user feedback

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Special thanks to the open-source community for the tools and libraries used
