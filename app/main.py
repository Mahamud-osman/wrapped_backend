from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse
from typing import Dict, Any, List
import os
from dotenv import load_dotenv

from .spotify_client import SpotifyClient
from .auth import create_access_token, get_current_user_tokens
from .models import SpotifyUser, Artist, Track, UserStats, TokenResponse
from .utils import extract_genres_from_artists, calculate_listening_trends, calculate_average_features

load_dotenv()

app = FastAPI(title="Spotify Wrapped So Far API", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:3000")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

spotify_client = SpotifyClient()

@app.get("/")
async def root():
    return {"message": "Spotify Wrapped So Far API"}

# Authentication endpoints
@app.get("/auth/login")
async def login():
    """Redirect to Spotify OAuth"""
    auth_url = spotify_client.get_auth_url()
    print(f"Generated auth URL: {auth_url}")
    print(f"Redirect URI: {spotify_client.redirect_uri}")
    return RedirectResponse(url=auth_url)

@app.get("/auth/callback")
async def auth_callback(code: str = None, error: str = None):
    """Handle Spotify OAuth callback"""
    if error:
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        return RedirectResponse(url=f"{frontend_url}?error={error}")
    
    if not code:
        raise HTTPException(status_code=400, detail="Authorization code not provided")
    
    try:
        # Exchange code for tokens
        tokens = spotify_client.exchange_code_for_tokens(code)
        
        # Get user profile to include in JWT
        user_profile = spotify_client.get_user_profile(tokens["access_token"])
        
        # Create JWT with Spotify tokens and user info
        token_data = {
            "sub": user_profile.id,
            "spotify_access_token": tokens["access_token"],
            "spotify_refresh_token": tokens["refresh_token"],
            "user_name": user_profile.display_name
        }
        
        jwt_token = create_access_token(token_data)
        
        # Redirect to frontend with token
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        return RedirectResponse(url=f"{frontend_url}/callback?token={jwt_token}")
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Authentication failed: {str(e)}")

@app.post("/auth/refresh")
async def refresh_token(tokens: Dict[str, str] = Depends(get_current_user_tokens)):
    """Refresh Spotify access token"""
    try:
        if not tokens.get("refresh_token"):
            raise HTTPException(status_code=400, detail="Refresh token not found")
        
        new_tokens = spotify_client.refresh_access_token(tokens["refresh_token"])
        
        # Create new JWT with updated tokens
        token_data = {
            "sub": tokens["user_id"],
            "spotify_access_token": new_tokens["access_token"],
            "spotify_refresh_token": tokens["refresh_token"]  # Keep original refresh token
        }
        
        jwt_token = create_access_token(token_data)
        
        return TokenResponse(
            access_token=jwt_token,
            refresh_token=tokens["refresh_token"],
            expires_in=new_tokens.get("expires_in", 3600)
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Token refresh failed: {str(e)}")

# Protected API endpoints
@app.get("/api/me", response_model=SpotifyUser)
async def get_user_profile(tokens: Dict[str, str] = Depends(get_current_user_tokens)):
    """Get current user's profile"""
    try:
        user = spotify_client.get_user_profile(tokens["access_token"])
        return user
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get user profile: {str(e)}")

@app.get("/api/top-artists", response_model=List[Artist])
async def get_top_artists(
    time_range: str = "medium_term",
    limit: int = 20,
    tokens: Dict[str, str] = Depends(get_current_user_tokens)
):
    """Get user's top artists"""
    try:
        artists = spotify_client.get_top_artists(tokens["access_token"], time_range, limit)
        return artists
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get top artists: {str(e)}")

@app.get("/api/top-tracks", response_model=List[Track])
async def get_top_tracks(
    time_range: str = "medium_term",
    limit: int = 20,
    tokens: Dict[str, str] = Depends(get_current_user_tokens)
):
    """Get user's top tracks with audio features"""
    try:
        tracks = spotify_client.get_top_tracks(tokens["access_token"], time_range, limit)
        return tracks
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get top tracks: {str(e)}")

@app.get("/api/recent")
async def get_recent_tracks(
    limit: int = 50,
    tokens: Dict[str, str] = Depends(get_current_user_tokens)
):
    """Get recently played tracks"""
    try:
        recent_tracks = spotify_client.get_recently_played(tokens["access_token"], limit)
        return [{"played_at": track.played_at, "track": track.track} for track in recent_tracks]
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get recent tracks: {str(e)}")

@app.get("/api/stats", response_model=UserStats)
async def get_user_stats(tokens: Dict[str, str] = Depends(get_current_user_tokens)):
    """Get aggregated user statistics"""
    try:
        print("Fetching user stats...")
        
        # Get data from Spotify with smaller limits first
        print("Getting top artists...")
        top_artists = spotify_client.get_top_artists(tokens["access_token"], limit=20)
        print(f"Got {len(top_artists)} artists")
        
        print("Getting top tracks...")
        top_tracks = spotify_client.get_top_tracks(tokens["access_token"], limit=20)
        print(f"Got {len(top_tracks)} tracks")
        
        print("Getting recent tracks...")
        recent_tracks = spotify_client.get_recently_played(tokens["access_token"], limit=20)
        print(f"Got {len(recent_tracks)} recent tracks")
        
        # Calculate total listening time (approximate from recent tracks)
        total_listening_time = sum(track.track.duration_ms for track in recent_tracks) if recent_tracks else 0
        print(f"Total listening time: {total_listening_time}")
        
        # Extract genres from top artists
        artists_data = [{"genres": artist.genres} for artist in top_artists]
        genre_counts = extract_genres_from_artists(artists_data)
        top_genres = [{"genre": genre, "count": count} for genre, count in 
                     sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)[:10]]
        print(f"Top genres: {len(top_genres)}")
        
        # Calculate listening trends
        recent_tracks_data = [{"played_at": track.played_at.isoformat()} for track in recent_tracks]
        listening_trends = calculate_listening_trends(recent_tracks_data)
        print(f"Listening trends: {listening_trends}")
        
        # Get audio features for top tracks (try with smaller batch)
        track_ids = [track.id for track in top_tracks[:10]]  # Limit to 10 tracks
        print(f"Getting audio features for {len(track_ids)} tracks...")
        audio_features = spotify_client.get_audio_features(tokens["access_token"], track_ids)
        print(f"Got {len(audio_features)} audio features")
        
        # Calculate average audio features
        features_data = [
            {
                "danceability": f.danceability,
                "energy": f.energy,
                "valence": f.valence,
                "tempo": f.tempo,
                "acousticness": f.acousticness,
                "instrumentalness": f.instrumentalness,
                "liveness": f.liveness,
                "speechiness": f.speechiness
            }
            for f in audio_features
        ]
        average_features = calculate_average_features(features_data)
        print(f"Average features: {average_features}")
        
        # Calculate mood score (average of valence and energy)
        mood_score = (average_features.get("valence", 0) + average_features.get("energy", 0)) / 2
        print(f"Mood score: {mood_score}")
        
        result = UserStats(
            total_listening_time_ms=total_listening_time,
            top_genres=top_genres,
            listening_trends=listening_trends,
            average_features=average_features,
            mood_score=mood_score
        )
        
        print("Stats calculation completed successfully")
        return result
        
    except Exception as e:
        print(f"Error in get_user_stats: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=f"Failed to get user stats: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)