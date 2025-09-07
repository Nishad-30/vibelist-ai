"""
Thematic Playlist Generator - Streamlit App
An Agentic AI Music Curator that creates perfect playlists for any vibe
"""

import streamlit as st
import json
import os
from music_curator import MusicCurator
from spotify_client import SpotifyClient
import config

# Page configuration
st.set_page_config(
    page_title="🎵 Thematic Playlist Generator",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #1DB954, #1ed760);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .vibe-input {
        font-size: 1.2rem;
        padding: 1rem;
        border-radius: 10px;
        border: 2px solid #1DB954;
    }
    .track-card {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #1DB954;
    }
    .ai-insight {
        background: #e8f4fd;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #0066cc;
        margin: 1rem 0;
    }
    .spotify-feedback {
        background: #fff3cd;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #ffc107;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'curator' not in st.session_state:
        st.session_state.curator = MusicCurator()
    if 'spotify_client' not in st.session_state:
        st.session_state.spotify_client = SpotifyClient()
    if 'playlist_history' not in st.session_state:
        st.session_state.playlist_history = []
    if 'spotify_authenticated' not in st.session_state:
        st.session_state.spotify_authenticated = False

def display_header():
    """Display the main header"""
    st.markdown("""
    <div class="main-header">
        <h1>🎵 Thematic Playlist Generator</h1>
        <p>Your AI Music Curator - Crafting Perfect Playlists for Any Vibe</p>
    </div>
    """, unsafe_allow_html=True)

def display_sidebar():
    """Display sidebar with information and controls"""
    st.sidebar.header("🤖 AI Music Curator")
    st.sidebar.markdown("""
    **How it works:**
    1. 🎯 Enter your vibe or mood
    2. 🧠 AI interprets your description
    3. 🎵 Generates curated song suggestions
    4. 🔄 Collaborates with Spotify for refinement
    5. ✨ Creates your perfect playlist
    """)
    
    st.sidebar.header("🎛️ Settings")
    
    # Spotify Authentication
    st.sidebar.subheader("Spotify Integration")
    if st.sidebar.button("🔗 Connect to Spotify"):
        with st.spinner("Connecting to Spotify..."):
            success = st.session_state.spotify_client.authenticate()
            if success:
                st.session_state.spotify_authenticated = True
                st.sidebar.success("✅ Connected to Spotify!")
            else:
                st.sidebar.error("❌ Spotify connection failed")
    
    if st.session_state.spotify_authenticated:
        st.sidebar.success("🟢 Spotify Connected")
    else:
        st.sidebar.warning("🟡 Spotify Not Connected")
        st.sidebar.info("Add your Spotify credentials to config.py")
    
    # Model Training
    st.sidebar.subheader("AI Model")
    if os.path.exists(config.MODEL_PATH):
        st.sidebar.success("✅ AI Model Loaded")
    else:
        st.sidebar.warning("⚠️ AI Model Not Found")
        if st.sidebar.button("🧠 Train AI Model"):
            train_model()
    
    # Playlist Settings
    st.sidebar.subheader("Playlist Settings")
    playlist_size = st.sidebar.slider("Playlist Size", 10, 50, config.DEFAULT_PLAYLIST_SIZE)
    return playlist_size

def train_model():
    """Train the AI model"""
    try:
        with st.spinner("Training AI Music Curator..."):
            import subprocess
            result = subprocess.run(['python', 'train_model.py'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                st.success("✅ AI Model trained successfully!")
                st.session_state.curator = MusicCurator()  # Reload curator
            else:
                st.error(f"❌ Training failed: {result.stderr}")
    except Exception as e:
        st.error(f"Training error: {str(e)}")

def display_ai_interpretation(interpretation):
    """Display AI's interpretation of the vibe"""
    st.markdown('<div class="ai-insight">', unsafe_allow_html=True)
    st.subheader("🧠 AI Interpretation")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Energy Level", f"{interpretation['energy']:.2f}")
        st.write("**Genres:**")
        for genre in interpretation['primary_genres'][:3]:
            st.write(f"• {genre}")
    
    with col2:
        st.metric("Mood (Valence)", f"{interpretation['valence']:.2f}")
        st.write(f"**Tempo:** {interpretation['tempo']}")
    
    with col3:
        st.write("**Characteristics:**")
        for char in interpretation['characteristics'][:4]:
            st.write(f"• {char}")
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_playlist(tracks, spotify_feedback=None):
    """Display the generated playlist"""
    st.subheader("🎵 Your Curated Playlist")
    
    if spotify_feedback:
        st.markdown('<div class="spotify-feedback">', unsafe_allow_html=True)
        st.write("🔄 **Collaborative AI Refinement:** Some suggestions were enhanced using Spotify's catalog")
        st.markdown('</div>', unsafe_allow_html=True)
    
    for i, track in enumerate(tracks, 1):
        st.markdown('<div class="track-card">', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 4, 2])
        
        with col1:
            st.write(f"**{i}.**")
        
        with col2:
            st.write(f"**{track['name']}**")
            st.write(f"by {track['artist']}")
            if track.get('source') == 'spotify_feedback':
                st.write("🔄 *AI-Refined Suggestion*")
        
        with col3:
            if track.get('external_url'):
                st.markdown(f"[🎵 Play on Spotify]({track['external_url']})")
            if track.get('preview_url'):
                st.audio(track['preview_url'])
        
        st.markdown('</div>', unsafe_allow_html=True)

def generate_playlist(vibe_description, playlist_size):
    """Generate playlist using AI curator and Spotify collaboration"""
    
    # Step 1: AI interprets the vibe
    with st.spinner("🧠 AI is interpreting your vibe..."):
        interpretation = st.session_state.curator.interpret_vibe(vibe_description)
    
    display_ai_interpretation(interpretation)
    
    # Step 2: Generate initial suggestions
    with st.spinner("🎵 Curating your playlist..."):
        initial_suggestions = st.session_state.curator.generate_song_suggestions(interpretation)
    
    # Step 3: Collaborate with Spotify (if connected)
    if st.session_state.spotify_authenticated:
        with st.spinner("🔄 Collaborating with Spotify for refinement..."):
            found_tracks, spotify_feedback = st.session_state.spotify_client.validate_and_enhance_playlist(
                initial_suggestions[:playlist_size]
            )
            
            if spotify_feedback:
                # Step 4: Refine suggestions based on Spotify feedback
                refined_suggestions = st.session_state.curator.generate_song_suggestions(
                    interpretation, spotify_feedback
                )
                
                # Combine found tracks with refined suggestions
                final_tracks = found_tracks + refined_suggestions
                final_tracks = final_tracks[:playlist_size]  # Limit to desired size
                
                display_playlist(final_tracks, spotify_feedback)
            else:
                display_playlist(found_tracks)
    else:
        # Display AI suggestions without Spotify validation
        st.info("💡 Connect to Spotify for real track validation and enhanced suggestions!")
        
        # Convert AI suggestions to display format
        display_tracks = []
        for suggestion in initial_suggestions[:playlist_size]:
            display_tracks.append({
                'name': suggestion['song'],
                'artist': suggestion['artist'],
                'external_url': None,
                'preview_url': None
            })
        
        display_playlist(display_tracks)
    
    # Save to history
    st.session_state.playlist_history.append({
        'vibe': vibe_description,
        'interpretation': interpretation,
        'timestamp': str(st.session_state.get('timestamp', 'now'))
    })

def display_playlist_history():
    """Display playlist generation history"""
    if st.session_state.playlist_history:
        st.subheader("📚 Playlist History")
        
        for i, entry in enumerate(reversed(st.session_state.playlist_history[-5:]), 1):
            with st.expander(f"🎵 {entry['vibe'][:50]}..."):
                st.write(f"**Vibe:** {entry['vibe']}")
                st.write(f"**Energy:** {entry['interpretation']['energy']:.2f}")
                st.write(f"**Mood:** {entry['interpretation']['valence']:.2f}")
                st.write(f"**Genres:** {', '.join(entry['interpretation']['primary_genres'][:3])}")

def main():
    """Main application"""
    initialize_session_state()
    display_header()
    
    # Sidebar
    playlist_size = display_sidebar()
    
    # Main content
    st.header("🎯 Describe Your Vibe")
    
    # Vibe input
    vibe_examples = [
        "late-night coding session",
        "rainy day focus", 
        "upbeat 80s workout",
        "morning coffee ritual",
        "road trip adventure",
        "romantic dinner",
        "study session deep focus",
        "party night energy"
    ]
    
    selected_example = st.selectbox(
        "Or choose from examples:",
        [""] + vibe_examples
    )
    
    vibe_input = st.text_area(
        "Enter your vibe, mood, or activity:",
        value=selected_example,
        height=100,
        placeholder="e.g., 'chill Sunday morning with coffee and books' or 'intense workout motivation'"
    )
    
    # Generate button
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        generate_button = st.button("🎵 Generate Playlist", type="primary")
    
    # Generate playlist
    if generate_button and vibe_input.strip():
        generate_playlist(vibe_input.strip(), playlist_size)
    elif generate_button:
        st.warning("⚠️ Please enter a vibe description!")
    
    # Display history
    if st.session_state.playlist_history:
        st.markdown("---")
        display_playlist_history()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 2rem;">
        <p>🤖 Powered by Custom AI Music Curator | 🎵 Enhanced by Spotify API</p>
        <p>Built with Streamlit | Train your own AI model for personalized curation</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()