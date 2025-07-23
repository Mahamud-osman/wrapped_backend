import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import os

# Set test environment variables
os.environ.update({
    "SPOTIFY_CLIENT_ID": "test_client_id",
    "SPOTIFY_CLIENT_SECRET": "test_client_secret", 
    "SPOTIFY_REDIRECT_URI": "http://localhost:8000/auth/callback",
    "JWT_SECRET": "test_jwt_secret",
    "FRONTEND_URL": "http://localhost:3000"
})

from app.main import app

@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)

@pytest.fixture
def mock_spotify_client():
    """Mock Spotify client for testing"""
    with patch('app.main.spotify_client') as mock:
        yield mock

@pytest.fixture
def sample_user_data():
    """Sample user data for testing"""
    return {
        "id": "test_user_123",
        "display_name": "Test User",
        "email": "test@example.com",
        "images": [{"url": "https://example.com/avatar.jpg"}],
        "followers": {"total": 100}
    }

@pytest.fixture
def sample_artists_data():
    """Sample artists data for testing"""
    return [
        {
            "id": "artist_1",
            "name": "Test Artist 1",
            "genres": ["pop", "rock"],
            "popularity": 80,
            "images": [{"url": "https://example.com/artist1.jpg"}],
            "external_urls": {"spotify": "https://spotify.com/artist1"}
        },
        {
            "id": "artist_2", 
            "name": "Test Artist 2",
            "genres": ["jazz", "blues"],
            "popularity": 60,
            "images": [{"url": "https://example.com/artist2.jpg"}],
            "external_urls": {"spotify": "https://spotify.com/artist2"}
        }
    ]

@pytest.fixture
def sample_tracks_data():
    """Sample tracks data for testing"""
    return [
        {
            "id": "track_1",
            "name": "Test Track 1",
            "artists": [{"id": "artist_1", "name": "Test Artist 1"}],
            "album": {
                "name": "Test Album 1",
                "images": [{"url": "https://example.com/album1.jpg"}]
            },
            "duration_ms": 180000,
            "popularity": 75,
            "external_urls": {"spotify": "https://spotify.com/track1"}
        }
    ]

@pytest.fixture
def valid_jwt_token():
    """Generate valid JWT token for testing"""
    from app.auth import create_access_token
    token_data = {
        "sub": "test_user_123",
        "spotify_access_token": "test_access_token",
        "spotify_refresh_token": "test_refresh_token"
    }
    return create_access_token(token_data)