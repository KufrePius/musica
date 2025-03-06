import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd

# Set up Spotify API credentials
CLIENT_ID = "b7d7f763070444d6975c29366ff0429b"
CLIENT_SECRET = "90519bc8ebef49d4b5a158a10a3a8456"

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET))

def get_song_details(song_name):
    results = sp.search(q=song_name, limit=1)
    if results["tracks"]["items"]:
        song = results["tracks"]["items"][0]
        return {
            "id": song["id"],
            "name": song["name"],
            "artist": song["artists"][0]["name"],
            "popularity": song["popularity"],
            "preview_url": song["preview_url"],
            "image_url": song["album"]["images"][0]["url"]
        }
    return None

def get_recommendations(song_id, genre=None, danceability=None, energy=None):
    seed_params = {"seed_tracks": [song_id], "limit": 5}
    
    if genre:
        seed_params["seed_genres"] = [genre]
    
    recs = sp.recommendations(**seed_params)
    recommendations = []
    
    for track in recs['tracks']:
        audio_features = sp.audio_features(track['id'])[0]
        
        if danceability and abs(audio_features['danceability'] - danceability) > 0.2:
            continue
        if energy and abs(audio_features['energy'] - energy) > 0.2:
            continue
        
        recommendations.append({
            "name": track["name"],
            "artist": track["artists"][0]["name"],
            "preview_url": track["preview_url"],
            "image_url": track["album"]["images"][0]["url"]
        })
    
    return recommendations

st.title("🎵 AI Music Recommender (Spotify API)")
st.write("Enter a song name and get recommendations based on genre, mood, and danceability!")

song_input = st.text_input("Enter a song title:")
genre_input = st.text_input("Enter a genre (optional):")
danceability_input = st.slider("Select Danceability (0 to 1, optional):", 0.0, 1.0, 0.5)
energy_input = st.slider("Select Energy Level (0 to 1, optional):", 0.0, 1.0, 0.5)

if song_input:
    song_info = get_song_details(song_input)
    if song_info:
        st.image(song_info["image_url"], width=300)
        st.write(f"🎶 Now Playing: **{song_info['name']}** by **{song_info['artist']}**")
        if song_info["preview_url"]:
            st.audio(song_info["preview_url"], format="audio/mp3")

        recs = get_recommendations(song_info['id'], genre_input, danceability_input, energy_input)
        st.write("🎵 **Recommended Songs:**")
        for track in recs:
            st.image(track["image_url"], width=100)
            st.write(f"**{track['name']}** by {track['artist']}")
            if track["preview_url"]:
                st.audio(track["preview_url"], format="audio/mp3")
    else:
        st.write("❌ Song not found. Try another one!")
