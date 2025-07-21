# Wrapped Backend

A FastAPI backend service for Spotify Wrapped application that handles OAuth authentication and provides Spotify API integration.

## Features

- Spotify OAuth 2.0 authentication
- JWT token management
- Spotify API integration for user data
- User profile and listening statistics
- Top artists and tracks retrieval
- Docker support for deployment

## Tech Stack

- **Framework**: FastAPI
- **Authentication**: JWT with Spotify OAuth
- **Database**: (Currently using in-memory storage)
- **Deployment**: Docker, Railway
- **Testing**: pytest

## Prerequisites

- Python 3.8+
- Spotify Developer Account
- Spotify App credentials (Client ID and Client Secret)

## Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd wrapped_backend
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Configuration**
   - Copy `.env.example` to `.env`
   - Fill in your Spotify credentials:
   ```env
   SPOTIFY_CLIENT_ID=your_spotify_client_id
   SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
   JWT_SECRET_KEY=your_jwt_secret_key
   ```

4. **Spotify App Setup**
   - Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
   - Create a new app
   - Add redirect URI: `http://localhost:8000/auth/callback`
   - Copy Client ID and Client Secret to your `.env` file

## Running the Application

### Development
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Docker
```bash
docker build -t wrapped-backend .
docker run -p 8000:8000 wrapped-backend
```

## API Endpoints

### Authentication
- `GET /auth/login` - Initiate Spotify OAuth flow
- `GET /auth/callback` - Handle OAuth callback
- `GET /auth/logout` - Logout user

### User Data
- `GET /api/me` - Get user profile (requires auth)
- `GET /api/top-artists` - Get user's top artists (requires auth)
- `GET /api/top-tracks` - Get user's top tracks (requires auth)
- `GET /api/stats` - Get user's listening statistics (requires auth)

## API Documentation

Once the server is running, you can access:
- Interactive API docs: http://localhost:8000/docs
- ReDoc documentation: http://localhost:8000/redoc

## Testing

Run tests with pytest:
```bash
pytest
```

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI application
│   ├── auth.py          # Authentication logic
│   ├── models.py        # Data models
│   ├── spotify_client.py # Spotify API client
│   └── utils.py         # Utility functions
├── tests/
│   └── test_auth_callback.py
├── Dockerfile
├── requirements.txt
├── requirements-prod.txt
└── README.md
```

## Deployment

### Railway
The project includes Railway configuration files for easy deployment:
- `railway.json` - Railway service configuration
- `railway.toml` - Railway project settings

### Environment Variables for Production
Make sure to set these environment variables in your production environment:
- `SPOTIFY_CLIENT_ID`
- `SPOTIFY_CLIENT_SECRET`
- `JWT_SECRET_KEY`
- `REDIRECT_URI` (your production callback URL)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License. 