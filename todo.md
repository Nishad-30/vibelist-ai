# Thematic Playlist Generator - MVP Implementation Plan

## Core Components

### 1. Model Training Pipeline (`train_model.py`)
- Simple text classification model using scikit-learn
- Training data with mood/vibe descriptions and corresponding music genres/characteristics
- Feature extraction using TfidfVectorizer
- Model serialization for deployment

### 2. AI Music Curator (`music_curator.py`)
- Load trained model for vibe interpretation
- Genre/mood mapping logic
- Song suggestion algorithms based on predicted characteristics
- Integration point for Spotify API feedback loop

### 3. Spotify API Integration (`spotify_client.py`)
- Spotify Web API client setup
- Search functionality for songs and artists
- Playlist creation capabilities
- Error handling for missing tracks

### 4. Main Streamlit App (`app.py`)
- User interface for vibe input
- Display generated playlists
- Spotify authentication flow
- Real-time feedback loop visualization

### 5. Configuration (`config.py`)
- API keys and settings
- Model parameters
- Genre mappings

### 6. Requirements (`requirements.txt`)
- All necessary dependencies

## Implementation Strategy
- Start with pre-built training data for common moods/vibes
- Use lightweight ML model (TF-IDF + Random Forest)
- Implement collaborative loop: AI suggests → Spotify validates → AI refines
- Simple but functional UI with Streamlit

## Files to Create (Max 8 files - HARD LIMIT)
1. `app.py` - Main Streamlit application
2. `train_model.py` - Model training script
3. `music_curator.py` - AI curator logic
4. `spotify_client.py` - Spotify API integration
5. `config.py` - Configuration settings
6. `requirements.txt` - Dependencies
7. `training_data.json` - Sample training data
8. `README.md` - Setup and deployment instructions