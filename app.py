"""
Thematic Playlist Generator - Streamlit App
An Agentic AI Music Curator that creates perfect playlists for any vibe
"""

import streamlit as st
import os
import subprocess
from datetime import datetime
from music_curator import MusicCurator
from spotify_client import SpotifyClient
import config

# --- Page Configuration ---
st.set_page_config(
    page_title="🎵 Thematic Playlist Generator",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS Styling ---
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
    .track-card {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 5px solid #1DB954;
        transition: background-color 0.3s ease;
    }
    .track-card:hover {
        background-color: #e9ecef;
    }
    .ai-insight {
        background: #e8f4fd;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #0066cc;
        margin: 1rem 0;
    }
    .spotify-feedback {
        background: #fff3cd;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #ffc107;
        margin: 1rem 0;
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        font-size: 1.1rem;
        padding: 0.75rem 0;
    }
</style>
""", unsafe_allow_html=True)


# --- Session State Initialization ---
def initialize_session_state():
    """Initialize session state variables safely."""
    if 'curator' not in st.session_state:
        try:
            st.session_state.curator = MusicCurator()
            st.session_state.model_loaded = True
        except Exception as e:
            st.session_state.curator = None
            st.session_state.model_loaded = False
            st.session_state.model_error = e

    if 'spotify_client' not in st.session_state:
        st.session_state.spotify_client = SpotifyClient()
    if 'playlist_history' not in st.session_state:
        st.session_state.playlist_history = []
    if 'spotify_authenticated' not in st.session_state:
        st.session_state.spotify_authenticated = False


# --- UI Components ---
def display_header():
    """Display the main header and title."""
    st.markdown("""
    <div class="main-header">
        <h1>🎵 Thematic Playlist Generator</h1>
        <p>Your AI Music Curator - Crafting Perfect Playlists for Any Vibe</p>
    </div>
    """, unsafe_allow_html=True)

def display_sidebar():
    """Display sidebar with information and controls."""
    st.sidebar.header("🤖 How It Works")
    st.sidebar.markdown("""
    1.  **🎯 Describe Your Vibe:** Enter any mood, activity, or theme.
    2.  **🧠 AI Interpretation:** The curator analyzes your vibe to predict key musical attributes.
    3.  **🎵 Initial Curation:** A list of song suggestions is generated from its knowledge base.
    4.  **🔄 Spotify Collaboration:** If connected, the app validates songs and refines suggestions with real-time Spotify data.
    5.  **✨ Playlist Created:** Your final, enhanced playlist is ready to enjoy.
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
                st.rerun()
            else:
                st.sidebar.error("❌ Spotify connection failed. Check credentials.")

    if st.session_state.spotify_authenticated:
        st.sidebar.success("🟢 Spotify Connected")
    else:
        st.sidebar.warning("🟡 Spotify Not Connected")
        st.sidebar.info("Connect to validate songs and get enhanced recommendations.")

    # Model Training Section
    st.sidebar.subheader("AI Model")
    if os.path.exists(config.MODEL_PATH):
        st.sidebar.success("✅ AI Model Loaded")
    else:
        st.sidebar.warning("⚠️ AI Model Not Found")

    if st.sidebar.button("🧠 Retrain AI Model"):
        st.sidebar.info("""
        Training is resource-intensive. On Streamlit Cloud, this may fail if it exceeds memory limits.
        Recommended for local execution.
        """)
        train_model()

    # Playlist Settings
    st.sidebar.subheader("Playlist Settings")
    playlist_size = st.sidebar.slider("Playlist Size", 10, 50, config.DEFAULT_PLAYLIST_SIZE, 5)
    return playlist_size

def display_ai_interpretation(interpretation):
    """Display AI's interpretation of the vibe in metric cards."""
    st.markdown('<div class="ai-insight">', unsafe_allow_html=True)
    st.subheader("🧠 AI Interpretation of Your Vibe")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Energy Level", f"{interpretation['energy']:.2f}")
        st.metric("Mood (Valence)", f"{interpretation['valence']:.2f}")
    with col2:
        st.write("**Predicted Genres:**")
        for genre in interpretation['primary_genres'][:3]:
            st.write(f"• {genre.title()}")
    with col3:
        st.write("**Predicted Characteristics:**")
        for char in interpretation['characteristics'][:4]:
            st.write(f"• {char.title()}")
    st.markdown('</div>', unsafe_allow_html=True)

def display_playlist(tracks, spotify_feedback=None):
    """Display the generated playlist with track cards."""
    st.subheader("🎵 Your Curated Playlist")

    if spotify_feedback:
        st.markdown('<div class="spotify-feedback">', unsafe_allow_html=True)
        st.write("🔄 **Collaborative AI Refinement:** Suggestions were enhanced using Spotify's catalog.")
        st.markdown('</div>', unsafe_allow_html=True)

    for i, track in enumerate(tracks, 1):
        st.markdown('<div class="track-card">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 4, 2])
        with col1:
            st.write(f"### {i}")
        with col2:
            st.write(f"**{track['name']}**")
            st.write(f"by {track['artist']}")
            if track.get('source') == 'spotify_feedback':
                st.write("🔄 *AI-Refined Suggestion*")
        with col3:
            if track.get('external_url'):
                st.link_button("Play on Spotify", track['external_url'])
            if track.get('preview_url'):
                st.audio(track['preview_url'])
        st.markdown('</div>', unsafe_allow_html=True)

def display_playlist_history():
    """Display recent playlist generation history in expanders."""
    if st.session_state.playlist_history:
        st.subheader("📚 Playlist History")
        # Show last 5 entries in reverse chronological order
        for entry in reversed(st.session_state.playlist_history[-5:]):
            with st.expander(f"🎵 **Vibe:** {entry['vibe'][:50]}..."):
                st.write(f"**Full Vibe:** {entry['vibe']}")
                st.write(f"**Timestamp:** {entry['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
                interp = entry['interpretation']
                st.write(f"**AI Interpretation:** Energy {interp['energy']:.2f}, Mood {interp['valence']:.2f}, Genres: {', '.join(interp['primary_genres'][:3])}")


# --- Core Logic ---
def train_model():
    """Train the AI model via an external script and reload the curator."""
    try:
        with st.spinner("Training AI Music Curator... This may take a few minutes."):
            result = subprocess.run(
                ['python', 'train_model.py'],
                capture_output=True, text=True, check=True
            )
            st.success("✅ AI Model trained successfully!")
            # Safely reload the curator instance
            try:
                st.session_state.curator = MusicCurator()
                st.session_state.model_loaded = True
                st.sidebar.success("Curator reloaded!")
            except Exception as e:
                st.session_state.model_loaded = False
                st.session_state.model_error = e
                st.error(f"Failed to reload curator after training: {e}")

    except subprocess.CalledProcessError as e:
        st.error(f"❌ Training failed with return code {e.returncode}")
        st.code(e.stderr, language='bash')
    except Exception as e:
        st.error(f"An unexpected error occurred during training: {str(e)}")

def generate_playlist(vibe_description, playlist_size):
    """Orchestrate the playlist generation process."""
    # Step 1: AI interprets the vibe
    with st.spinner("🧠 AI is interpreting your vibe..."):
        interpretation = st.session_state.curator.interpret_vibe(vibe_description)
    display_ai_interpretation(interpretation)

    # Step 2: Generate initial suggestions
    with st.spinner("🎵 Curating initial song suggestions..."):
        initial_suggestions = st.session_state.curator.generate_song_suggestions(interpretation)

    # Step 3: Collaborate with Spotify if connected
    if st.session_state.spotify_authenticated:
        with st.spinner("🔄 Collaborating with Spotify for refinement..."):
            found_tracks, spotify_feedback = st.session_state.spotify_client.validate_and_enhance_playlist(
                initial_suggestions, num_tracks=playlist_size
            )

        if spotify_feedback:
            # Step 4: Refine suggestions based on Spotify's feedback
            with st.spinner("✨ Refining suggestions based on feedback..."):
                refined_suggestions = st.session_state.curator.generate_song_suggestions(
                    interpretation, spotify_feedback
                )
                # Combine found tracks with newly refined suggestions
                final_tracks = found_tracks
                for track in refined_suggestions:
                    if len(final_tracks) < playlist_size:
                        final_tracks.append(track)
                    else:
                        break
                # Final validation pass on the combined list
                final_tracks, _ = st.session_state.spotify_client.validate_and_enhance_playlist(final_tracks, num_tracks=playlist_size)
        else:
            final_tracks = found_tracks

        display_playlist(final_tracks[:playlist_size], spotify_feedback)
    else:
        # Display AI suggestions without Spotify validation
        st.info("💡 Connect to Spotify for real track validation and enhanced suggestions!")
        display_tracks = [{
            'name': s['song'],
            'artist': s['artist'],
            'external_url': None,
            'preview_url': None
        } for s in initial_suggestions[:playlist_size]]
        display_playlist(display_tracks)

    # Save to history
    st.session_state.playlist_history.append({
        'vibe': vibe_description,
        'interpretation': interpretation,
        'timestamp': datetime.now()
    })


# --- Main Application ---
def main():
    """Main application flow."""
    initialize_session_state()
    display_header()

    # Critical check: Stop the app if the model isn't loaded.
    if not st.session_state.get('model_loaded', False):
        st.error(f"🚨 Critical Error: The AI model could not be loaded.")
        st.warning(f"Error details: {st.session_state.model_error}")
        st.info("The app is disabled. Please ensure the model file exists and the environment is correct, then refresh. You may need to retrain the model from the sidebar.")
        display_sidebar() # Display sidebar to allow retraining
        st.stop()

    # --- Layout ---
    playlist_size = display_sidebar()
    st.header("🎯 Describe Your Vibe")

    # Vibe input form
    vibe_examples = [
        "late-night coding session", "rainy day focus", "upbeat 80s workout",
        "morning coffee ritual", "road trip adventure", "romantic dinner",
        "study session deep focus", "summer beach party"
    ]
    selected_example = st.selectbox("Or choose from examples:", [""] + vibe_examples, help="Select a pre-defined vibe to get started.")
    vibe_input = st.text_area(
        "Enter your vibe, mood, or activity:",
        value=selected_example,
        height=100,
        placeholder="e.g., 'chill Sunday morning with coffee and books' or 'intense workout motivation'"
    )

    # Generate button
    _, col2, _ = st.columns([2, 1, 2])
    with col2:
        generate_button = st.button("🎵 Generate Playlist", type="primary", use_container_width=True)

    # --- Logic Execution ---
    if generate_button:
        final_vibe = vibe_input.strip()
        if final_vibe:
            generate_playlist(final_vibe, playlist_size)
        else:
            st.warning("⚠️ Please enter a vibe description!")

    # Display history
    if st.session_state.playlist_history:
        st.markdown("---")
        display_playlist_history()

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 2rem;">
        <p>🤖 Powered by a Custom AI Music Curator | 🎵 Enhanced by the Spotify API</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
