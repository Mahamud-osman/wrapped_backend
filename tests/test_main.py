import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from app.models import SpotifyUser, Artist, Track

def test_root_endpoint(client):
    """Test root endpoint returns correct message"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Spotify Wrapped So Far API"}

def test_auth_login_redirect(client, mock_spotify_client):
    """Test login endpoint redirects to Spotify"""
    mock_spotify_client.get_auth_url.return_value = "https://accounts.spotify.com/authorize?test=true"
    
    response = client.get("/auth/login", follow_redirects=False)
    assert response.status_code == 307
    assert "accounts.spotify.com" in response.headers["location"]

def test_auth_callback_success(client, mock_spotify_client, sample_user_data):
    """Test successful OAuth callback"""
    # Mock token exchange
    mock_spotify_client.exchange_code_for_tokens.return_value = {
        "access_token": "test_access_token",
        "refresh_token": "test_refresh_token"
    }
    
    # Mock user profile
    mock_user = SpotifyUser(**sample_user_data)
    mock_spotify_client.get_user_profile.return_value = mock_user
    
    response = client.get("/auth/callback?code=test_code", follow_redirects=False)
    assert response.status_code == 307
    assert "callback?token=" in response.headers["location"]

def test_auth_callback_error(client):
    """Test OAuth callback with error"""
    response = client.get("/auth/callback?error=access_denied", follow_redirects=False)
    assert response.status_code == 307
    assert "error=access_denied" in response.headers["location"]

def test_auth_callback_no_code(client):
    """Test OAuth callback without code"""
    response = client.get("/auth/callback")
    assert response.status_code == 400
    assert "Authorization code not provided" in response.json()["detail"]

def test_get_user_profile_success(client, mock_spotify_client, sample_user_data, valid_jwt_token):
    """Test getting user profile with valid token"""
    mock_user = SpotifyUser(**sample_user_data)
    mock_spotify_client.get_user_profile.return_value = mock_user
    
    headers = {"Authorization": f"Bearer {valid_jwt_token}"}
    response = client.get("/api/me", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "test_user_123"
    assert data["display_name"] == "Test User"

def test_get_user_profile_unauthorized(client):
    """Test getting user profile without token"""
    response = client.get("/api/me")
    assert response.status_code == 403

def test_get_top_artists_success(client, mock_spotify_client, sample_artists_data, valid_jwt_token):
    """Test getting top artists"""
    mock_artists = [Artist(**artist) for artist in sample_artists_data]
    mock_spotify_client.get_top_artists.return_value = mock_artists
    
    headers = {"Authorization": f"Bearer {valid_jwt_token}"}
    response = client.get("/api/top-artists?limit=6", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "Test Artist 1"

def test_get_top_tracks_success(client, mock_spotify_client, sample_tracks_data, valid_jwt_token):
    """Test getting top tracks"""
    mock_tracks = [Track(**track) for track in sample_tracks_data]
    mock_spotify_client.get_top_tracks.return_value = mock_tracks
    
    headers = {"Authorization": f"Bearer {valid_jwt_token}"}
    response = client.get("/api/top-tracks?limit=10", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Test Track 1"

def test_api_endpoint_with_invalid_token(client):
    """Test API endpoints with invalid token"""
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.get("/api/me", headers=headers)
    assert response.status_code == 401