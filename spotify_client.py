"""
Spotify API Client for the Thematic Playlist Generator
Handles authentication, search, and playlist creation
"""

import base64
import requests
import streamlit as st
from typing import List, Dict, Optional, Tuple
import config

class SpotifyClient:
    """Spotify Web API Client with collaborative feedback capabilities"""
    
    def __init__(self):
        self.access_token = None
        self.base_url = "https://api.spotify.com/v1"
        
    def authenticate(self) -> bool:
        """Authenticate with Spotify using Client Credentials flow"""
        try:
            # For demo purposes, we'll use client credentials flow
            # In production, you'd want to use Authorization Code flow for user playlists
            
            auth_url = "https://accounts.spotify.com/api/token"
            
            # Encode client credentials
            client_creds = f"{config.SPOTIFY_CLIENT_ID}:{config.SPOTIFY_CLIENT_SECRET}"
            client_creds_b64 = base64.b64encode(client_creds.encode()).decode()
            
            headers = {
                "Authorization": f"Basic {client_creds_b64}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            data = {"grant_type": "client_credentials"}
            
            response = requests.post(auth_url, headers=headers, data=data)
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data["access_token"]
                return True
            else:
                st.error(f"Authentication failed: {response.status_code}")
                return False
                
        except Exception as e:
            st.error(f"Authentication error: {str(e)}")
            return False
    
    def search_track(self, artist: str, song: str) -> Optional[Dict]:
        """Search for a specific track on Spotify"""
        if not self.access_token:
            return None
            
        query = f"artist:{artist} track:{song}"
        url = f"{self.base_url}/search"
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        params = {
            "q": query,
            "type": "track",
            "limit": 1
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                data = response.json()
                tracks = data.get("tracks", {}).get("items", [])
                if tracks:
                    track = tracks[0]
                    return {
                        "id": track["id"],
                        "name": track["name"],
                        "artist": track["artists"][0]["name"],
                        "uri": track["uri"],
                        "external_url": track["external_urls"]["spotify"],
                        "preview_url": track.get("preview_url"),
                        "popularity": track["popularity"]
                    }
            return None
        except Exception as e:
            st.error(f"Search error: {str(e)}")
            return None
    
    def search_similar_tracks(self, artist: str, genre: str, limit: int = 10) -> List[Dict]:
        """
        Search for similar tracks when original suggestion isn't found
        This provides feedback to the AI curator for collaborative refinement
        """
        if not self.access_token:
            return []
        
        # Search by artist first
        query = f"artist:{artist}"
        url = f"{self.base_url}/search"
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        params = {
            "q": query,
            "type": "track",
            "limit": limit
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                data = response.json()
                tracks = data.get("tracks", {}).get("items", [])
                
                similar_tracks = []
                for track in tracks:
                    similar_tracks.append({
                        "id": track["id"],
                        "name": track["name"],
                        "artist": track["artists"][0]["name"],
                        "uri": track["uri"],
                        "external_url": track["external_urls"]["spotify"],
                        "preview_url": track.get("preview_url"),
                        "popularity": track["popularity"],
                        "feedback_format": f"{track['artists'][0]['name']} - {track['name']}"
                    })
                
                return similar_tracks
            
            # If artist search fails, try genre-based search
            return self._search_by_genre(genre, limit)
            
        except Exception as e:
            st.error(f"Similar tracks search error: {str(e)}")
            return []
    
    def _search_by_genre(self, genre: str, limit: int = 10) -> List[Dict]:
        """Fallback search by genre"""
        query = f"genre:{genre}"
        url = f"{self.base_url}/search"
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        params = {
            "q": query,
            "type": "track",
            "limit": limit
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                data = response.json()
                tracks = data.get("tracks", {}).get("items", [])
                
                genre_tracks = []
                for track in tracks:
                    genre_tracks.append({
                        "id": track["id"],
                        "name": track["name"],
                        "artist": track["artists"][0]["name"],
                        "uri": track["uri"],
                        "external_url": track["external_urls"]["spotify"],
                        "preview_url": track.get("preview_url"),
                        "popularity": track["popularity"],
                        "feedback_format": f"{track['artists'][0]['name']} - {track['name']}"
                    })
                
                return genre_tracks
            
        except Exception as e:
            st.error(f"Genre search error: {str(e)}")
            
        return []
    
    def validate_and_enhance_playlist(self, suggestions: List[Dict]) -> Tuple[List[Dict], List[str]]:
        """
        Validate AI suggestions against Spotify and provide feedback
        Returns: (found_tracks, spotify_feedback_for_ai)
        """
        found_tracks = []
        spotify_feedback = []
        
        for suggestion in suggestions:
            artist = suggestion.get('artist', '')
            song = suggestion.get('song', '')
            genre = suggestion.get('genre', '')
            
            # Try to find the exact track
            found_track = self.search_track(artist, song)
            
            if found_track:
                found_tracks.append(found_track)
            else:
                # Track not found - get similar tracks for feedback
                similar_tracks = self.search_similar_tracks(artist, genre, limit=3)
                
                if similar_tracks:
                    # Add the best match to found tracks
                    best_match = similar_tracks[0]
                    found_tracks.append(best_match)
                    
                    # Provide feedback to AI curator
                    for track in similar_tracks[:2]:  # Top 2 alternatives
                        spotify_feedback.append(track['feedback_format'])
        
        return found_tracks, spotify_feedback
    
    def get_track_features(self, track_ids: List[str]) -> List[Dict]:
        """Get audio features for tracks (energy, valence, etc.)"""
        if not self.access_token or not track_ids:
            return []
        
        url = f"{self.base_url}/audio-features"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        params = {"ids": ",".join(track_ids)}
        
        try:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                data = response.json()
                return data.get("audio_features", [])
        except Exception as e:
            st.error(f"Audio features error: {str(e)}")
        
        return []
    
    def create_playlist_url(self, track_uris: List[str]) -> str:
        """Create a Spotify playlist URL for easy sharing"""
        # For demo purposes, create a search URL with the tracks
        # In production with user auth, you'd create an actual playlist
        track_names = []
        for uri in track_uris[:5]:  # Limit for URL length
            track_id = uri.split(":")[-1]
            track_names.append(track_id)
        
        search_query = " ".join(track_names)
        return f"https://open.spotify.com/search/{search_query}"