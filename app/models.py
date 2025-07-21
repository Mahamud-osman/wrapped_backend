from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class SpotifyUser(BaseModel):
    id: str
    display_name: str
    email: str
    images: List[Dict[str, Any]] = []
    followers: Dict[str, Any] = {}

class Artist(BaseModel):
    id: str
    name: str
    images: List[Dict[str, Any]] = []
    genres: List[str] = []
    popularity: int = 0
    external_urls: Dict[str, str] = {}

class Track(BaseModel):
    id: str
    name: str
    artists: List[Artist]
    album: Dict[str, Any]
    duration_ms: int
    popularity: int
    external_urls: Dict[str, str] = {}

class AudioFeatures(BaseModel):
    id: str
    danceability: float
    energy: float
    valence: float
    tempo: float
    acousticness: float
    instrumentalness: float
    liveness: float
    speechiness: float

class RecentTrack(BaseModel):
    played_at: datetime
    track: Track

class UserStats(BaseModel):
    total_listening_time_ms: int
    top_genres: List[Dict[str, Any]]
    listening_trends: Dict[int, int]  # hour -> count
    average_features: Dict[str, float]
    mood_score: float

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str = "Bearer"