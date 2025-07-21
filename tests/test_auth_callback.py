import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app

client = TestClient(app)

# Fake responses for mocking
fake_tokens = {
    "access_token": "fake-access-token",
    "refresh_token": "fake-refresh-token",
    "expires_in": 3600
}

fake_user_profile = type("User", (), {"id": "user123", "display_name": "Test User"})()

@patch("app.spotify_client.SpotifyClient.exchange_code_for_tokens", return_value=fake_tokens)
@patch("app.spotify_client.SpotifyClient.get_user_profile", return_value=fake_user_profile)
def test_auth_callback_success(mock_profile, mock_exchange):
    response = client.get("/auth/callback?code=fakecode", allow_redirects=False)
    # Should redirect to frontend with token in URL
    assert response.status_code == 307 or response.status_code == 302
    assert "callback?token=" in response.headers["location"] 