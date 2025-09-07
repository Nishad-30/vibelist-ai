"""Configuration settings for the Thematic Playlist Generator"""

import os
from typing import Dict, List

# Spotify API Configuration
SPOTIFY_CLIENT_ID = "c1d3899cb6d04fbe939e2c6a09f135b0"
SPOTIFY_CLIENT_SECRET = "09800c6ebfd14f54981cc58a750d3b14"
SPOTIFY_REDIRECT_URI = 'http://localhost:8501/callback'

# Model Configuration
MODEL_PATH = 'trained_model.pkl'
VECTORIZER_PATH = 'vectorizer.pkl'
TRAINING_DATA_PATH = 'training_data.json'

# Music Characteristics Mapping
GENRE_MAPPING = {
    'electronic': ['electronic', 'techno', 'house', 'ambient', 'downtempo'],
    'rock': ['rock', 'alternative rock', 'indie rock', 'classic rock'],
    'pop': ['pop', 'indie pop', 'synth-pop', 'electropop'],
    'jazz': ['jazz', 'smooth jazz', 'contemporary jazz', 'nu jazz'],
    'classical': ['classical', 'orchestral', 'chamber music', 'piano'],
    'hip-hop': ['hip hop', 'rap', 'trap', 'old school hip hop'],
    'indie': ['indie', 'indie folk', 'indie rock', 'indie pop'],
    'ambient': ['ambient', 'drone', 'dark ambient', 'space ambient'],
    'lo-fi': ['lo-fi', 'chillhop', 'lo-fi hip hop', 'bedroom pop'],
    'folk': ['folk', 'acoustic', 'singer-songwriter', 'americana'],
    'r&b': ['r&b', 'soul', 'neo soul', 'contemporary r&b'],
    'dance': ['dance', 'edm', 'house', 'trance', 'disco']
}

# Energy and Valence Ranges
ENERGY_RANGES = {
    'low': (0.0, 0.3),
    'medium-low': (0.3, 0.5),
    'medium': (0.5, 0.7),
    'high': (0.7, 1.0)
}

VALENCE_RANGES = {
    'sad': (0.0, 0.3),
    'neutral': (0.3, 0.7),
    'happy': (0.7, 1.0)
}

# Default Playlist Settings
DEFAULT_PLAYLIST_SIZE = 20
MAX_RETRIES = 3
SEARCH_LIMIT = 50