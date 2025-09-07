"""
AI Music Curator - The heart of the Thematic Playlist Generator
Acts as a world-class DJ and music curator
"""

import pickle
import numpy as np
from typing import List, Dict, Tuple
import config

class MusicCurator:
    """Agentic AI Music Curator"""
    
    def __init__(self):
        self.models = None
        self.load_models()
    
    def load_models(self):
        """Load trained ML models"""
        try:
            with open(config.MODEL_PATH, 'rb') as f:
                self.models = pickle.load(f)
            print("✅ AI Music Curator models loaded successfully!")
        except FileNotFoundError:
            print("❌ Models not found. Please run train_model.py first.")
            self.models = None
    
    def interpret_vibe(self, vibe_description: str) -> Dict:
        """
        Interpret user's vibe description using trained AI models
        Returns predicted genres, energy, valence, and characteristics
        """
        if not self.models:
            return self._fallback_interpretation(vibe_description)
        
        # Vectorize the input
        vectorizer = self.models['vectorizer']
        features = vectorizer.transform([vibe_description])
        
        # Predict genre
        genre_pred = self.models['genre_classifier'].predict(features)[0]
        genre_name = self.models['genre_encoder'].inverse_transform([genre_pred])[0]
        
        # Predict energy and valence
        energy = float(self.models['energy_regressor'].predict(features)[0])
        valence = float(self.models['valence_regressor'].predict(features)[0])
        
        # Ensure values are in valid range
        energy = max(0.0, min(1.0, energy))
        valence = max(0.0, min(1.0, valence))
        
        return {
            'primary_genres': self._expand_genres(genre_name),
            'energy': energy,
            'valence': valence,
            'tempo': self._energy_to_tempo(energy),
            'characteristics': self._derive_characteristics(vibe_description, energy, valence)
        }
    
    def _expand_genres(self, primary_genre: str) -> List[str]:
        """Expand primary genre to related genres"""
        genre_words = primary_genre.split()
        expanded = []
        
        for word in genre_words:
            if word in config.GENRE_MAPPING:
                expanded.extend(config.GENRE_MAPPING[word])
            else:
                expanded.append(word)
        
        return list(set(expanded))[:5]  # Limit to 5 genres
    
    def _energy_to_tempo(self, energy: float) -> str:
        """Convert energy level to tempo description"""
        if energy < 0.3:
            return "slow"
        elif energy < 0.6:
            return "medium"
        else:
            return "fast"
    
    def _derive_characteristics(self, vibe: str, energy: float, valence: float) -> List[str]:
        """Derive musical characteristics from vibe and predicted values"""
        characteristics = []
        
        # Energy-based characteristics
        if energy < 0.3:
            characteristics.extend(["calm", "peaceful", "relaxed"])
        elif energy > 0.7:
            characteristics.extend(["energetic", "upbeat", "dynamic"])
        else:
            characteristics.extend(["moderate", "balanced"])
        
        # Valence-based characteristics
        if valence < 0.3:
            characteristics.extend(["melancholy", "introspective", "emotional"])
        elif valence > 0.7:
            characteristics.extend(["happy", "uplifting", "positive"])
        else:
            characteristics.extend(["neutral", "contemplative"])
        
        # Context-based characteristics
        vibe_lower = vibe.lower()
        if any(word in vibe_lower for word in ["focus", "study", "work", "coding"]):
            characteristics.extend(["focus", "concentration", "minimal"])
        if any(word in vibe_lower for word in ["party", "dance", "workout"]):
            characteristics.extend(["danceable", "motivational"])
        if any(word in vibe_lower for word in ["romantic", "dinner", "date"]):
            characteristics.extend(["romantic", "intimate", "smooth"])
        
        return list(set(characteristics))[:6]  # Limit to 6 characteristics
    
    def generate_song_suggestions(self, interpretation: Dict, spotify_feedback: List[str] = None) -> List[Dict]:
        """
        Generate song suggestions based on interpretation
        Incorporates Spotify API feedback for collaborative refinement
        """
        suggestions = []
        
        # Base song suggestions based on interpretation
        base_suggestions = self._get_base_suggestions(interpretation)
        
        # If we have Spotify feedback, refine suggestions
        if spotify_feedback:
            refined_suggestions = self._refine_with_spotify_feedback(
                base_suggestions, spotify_feedback, interpretation
            )
            suggestions.extend(refined_suggestions)
        else:
            suggestions.extend(base_suggestions)
        
        return suggestions[:config.DEFAULT_PLAYLIST_SIZE]
    
    def _get_base_suggestions(self, interpretation: Dict) -> List[Dict]:
        """Generate base song suggestions using curated knowledge"""
        suggestions = []
        genres = interpretation['primary_genres']
        energy = interpretation['energy']
        valence = interpretation['valence']
        
        # Genre-based suggestions with energy/valence modifiers
        for genre in genres[:3]:  # Focus on top 3 genres
            genre_suggestions = self._get_genre_suggestions(genre, energy, valence)
            suggestions.extend(genre_suggestions)
        
        return suggestions
    
    def _get_genre_suggestions(self, genre: str, energy: float, valence: float) -> List[Dict]:
        """Get suggestions for a specific genre with energy/valence constraints"""
        # This is a simplified version - in a real system, you'd have a larger database
        genre_artists = {
            'electronic': ['Daft Punk', 'Aphex Twin', 'Boards of Canada', 'Tycho'],
            'rock': ['The Beatles', 'Led Zeppelin', 'Radiohead', 'Arctic Monkeys'],
            'jazz': ['Miles Davis', 'John Coltrane', 'Bill Evans', 'Herbie Hancock'],
            'ambient': ['Brian Eno', 'Stars of the Lid', 'Tim Hecker', 'Grouper'],
            'lo-fi': ['Nujabes', 'J Dilla', 'Emancipator', 'Bonobo'],
            'pop': ['The Weeknd', 'Billie Eilish', 'Taylor Swift', 'Dua Lipa'],
            'hip-hop': ['Kendrick Lamar', 'J. Cole', 'Tyler, The Creator', 'Mac Miller'],
            'indie': ['Tame Impala', 'Arctic Monkeys', 'The Strokes', 'Vampire Weekend']
        }
        
        suggestions = []
        artists = genre_artists.get(genre, [f'{genre} artist'])
        
        for artist in artists[:2]:  # 2 artists per genre
            # Generate hypothetical songs with energy/valence matching
            song_title = self._generate_song_title(genre, energy, valence)
            suggestions.append({
                'artist': artist,
                'song': song_title,
                'genre': genre,
                'energy': energy,
                'valence': valence,
                'confidence': 0.8
            })
        
        return suggestions
    
    def _generate_song_title(self, genre: str, energy: float, valence: float) -> str:
        """Generate contextual song titles (placeholder for real song matching)"""
        # This is simplified - real implementation would use actual song databases
        energy_words = ["Slow", "Gentle", "Moderate", "Energetic", "Intense"]
        valence_words = ["Blue", "Calm", "Neutral", "Bright", "Euphoric"]
        
        energy_idx = min(4, int(energy * 5))
        valence_idx = min(4, int(valence * 5))
        
        return f"{energy_words[energy_idx]} {valence_words[valence_idx]} {genre.title()}"
    
    def _refine_with_spotify_feedback(self, base_suggestions: List[Dict], 
                                    spotify_feedback: List[str], 
                                    interpretation: Dict) -> List[Dict]:
        """
        Collaborative refinement using Spotify API feedback
        When songs aren't found, use Spotify's suggestions to improve recommendations
        """
        refined_suggestions = []
        
        # Process Spotify feedback to extract new artists/songs
        for feedback_item in spotify_feedback:
            # Parse Spotify feedback (artist - song format)
            if ' - ' in feedback_item:
                artist, song = feedback_item.split(' - ', 1)
                refined_suggestions.append({
                    'artist': artist.strip(),
                    'song': song.strip(),
                    'genre': 'spotify_suggested',
                    'energy': interpretation['energy'],
                    'valence': interpretation['valence'],
                    'confidence': 0.9,
                    'source': 'spotify_feedback'
                })
        
        # Combine with original suggestions, prioritizing Spotify feedback
        all_suggestions = refined_suggestions + base_suggestions
        
        return all_suggestions
    
    def _fallback_interpretation(self, vibe_description: str) -> Dict:
        """Fallback interpretation when models aren't available"""
        vibe_lower = vibe_description.lower()
        
        # Simple rule-based interpretation
        if any(word in vibe_lower for word in ["energetic", "workout", "party", "upbeat"]):
            return {
                'primary_genres': ['pop', 'dance', 'electronic'],
                'energy': 0.8,
                'valence': 0.7,
                'tempo': 'fast',
                'characteristics': ['energetic', 'upbeat', 'danceable']
            }
        elif any(word in vibe_lower for word in ["calm", "relax", "chill", "ambient"]):
            return {
                'primary_genres': ['ambient', 'lo-fi', 'acoustic'],
                'energy': 0.3,
                'valence': 0.5,
                'tempo': 'slow',
                'characteristics': ['calm', 'peaceful', 'relaxed']
            }
        else:
            return {
                'primary_genres': ['indie', 'alternative', 'pop'],
                'energy': 0.5,
                'valence': 0.5,
                'tempo': 'medium',
                'characteristics': ['balanced', 'moderate']
            }