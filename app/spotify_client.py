import requests
import base64
import os
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from .utils import cache_response
from .models import SpotifyUser, Artist, Track, AudioFeatures, RecentTrack
from dotenv import load_dotenv

load_dotenv()

class SpotifyClient:
    def __init__(self):
        self.client_id = os.getenv("SPOTIFY_CLIENT_ID")
        self.client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
        self.redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI")
        self.base_url = "https://api.spotify.com/v1"
        self.auth_url = "https://accounts.spotify.com/api/token"
        self.authorize_url = "https://accounts.spotify.com/authorize"

    def get_auth_url(self) -> str:
        """Generate Spotify authorization URL"""
        scopes = [
            "user-top-read",
            "user-read-recently-played",
            "user-read-private",
            "user-read-email"
        ]
        
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "scope": " ".join(scopes),
            "show_dialog": "true"
        }
        
        from urllib.parse import urlencode
        query_string = urlencode(params)
        return f"{self.authorize_url}?{query_string}"

    def exchange_code_for_tokens(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access and refresh tokens"""
        auth_header = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()
        
        headers = {
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri
        }
        
        response = requests.post(self.auth_url, headers=headers, data=data)
        response.raise_for_status()
        return response.json()

    def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh access token using refresh token"""
        auth_header = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()
        
        headers = {
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }
        
        response = requests.post(self.auth_url, headers=headers, data=data)
        response.raise_for_status()
        return response.json()

    def _make_request(self, endpoint: str, access_token: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make authenticated request to Spotify API"""
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = requests.get(url, headers=headers, params=params or {})
        response.raise_for_status()
        return response.json()

    @cache_response(300)  # Cache for 5 minutes
    def get_user_profile(self, access_token: str) -> SpotifyUser:
        """Get current user's profile"""
        data = self._make_request("me", access_token)
        return SpotifyUser(**data)

    @cache_response(300)
    def get_top_artists(self, access_token: str, time_range: str = "medium_term", limit: int = 20) -> List[Artist]:
        """Get user's top artists"""
        params = {"time_range": time_range, "limit": limit}
        data = self._make_request("me/top/artists", access_token, params)
        return [Artist(**artist) for artist in data.get("items", [])]

    @cache_response(300)
    def get_top_tracks(self, access_token: str, time_range: str = "medium_term", limit: int = 20) -> List[Track]:
        """Get user's top tracks"""
        params = {"time_range": time_range, "limit": limit}
        data = self._make_request("me/top/tracks", access_token, params)
        tracks = []
        for track_data in data.get("items", []):
            track_data["artists"] = [Artist(**artist) for artist in track_data.get("artists", [])]
            tracks.append(Track(**track_data))
        return tracks

    @cache_response(300)
    def get_recently_played(self, access_token: str, limit: int = 50) -> List[RecentTrack]:
        """Get recently played tracks"""
        params = {"limit": limit}
        data = self._make_request("me/player/recently-played", access_token, params)
        
        recent_tracks = []
        for item in data.get("items", []):
            track_data = item["track"]
            track_data["artists"] = [Artist(**artist) for artist in track_data.get("artists", [])]
            track = Track(**track_data)
            
            recent_track = RecentTrack(
                played_at=datetime.fromisoformat(item["played_at"].replace('Z', '+00:00')),
                track=track
            )
            recent_tracks.append(recent_track)
        
        return recent_tracks

    @cache_response(300)
    def get_audio_features(self, access_token: str, track_ids: List[str]) -> List[AudioFeatures]:
        """Get audio features for multiple tracks"""
        if not track_ids:
            return []
        
        # Spotify API allows max 100 track IDs per request
        features = []
        for i in range(0, len(track_ids), 100):
            batch_ids = track_ids[i:i+100]
            params = {"ids": ",".join(batch_ids)}
            data = self._make_request("audio-features", access_token, params)
            
            for feature_data in data.get("audio_features", []):
                if feature_data:  # Some tracks might not have audio features
                    features.append(AudioFeatures(**feature_data))
        
        return features