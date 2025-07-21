import functools
import json
import time
from typing import Any, Dict, Optional
import redis
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Redis client (optional)
redis_client = None
redis_url = os.getenv("REDIS_URL")
if redis_url:
    try:
        redis_client = redis.from_url(redis_url)
        # Test the connection
        redis_client.ping()
        print("Redis connected successfully")
    except Exception as e:
        print(f"Redis connection failed: {e}. Continuing without caching.")
        redis_client = None

def cache_response(expiry_seconds: int = 300):
    """Decorator to cache API responses"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not redis_client:
                return func(*args, **kwargs)
            
            # Create cache key from function name and arguments
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            cached_result = redis_client.get(cache_key)
            if cached_result:
                return json.loads(cached_result)
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            redis_client.setex(cache_key, expiry_seconds, json.dumps(result, default=str))
            return result
        return wrapper
    return decorator

def extract_genres_from_artists(artists_data: list) -> Dict[str, int]:
    """Extract and count genres from artist data"""
    genre_count = {}
    for artist in artists_data:
        for genre in artist.get('genres', []):
            genre_count[genre] = genre_count.get(genre, 0) + 1
    return genre_count

def calculate_listening_trends(recent_tracks: list) -> Dict[int, int]:
    """Calculate listening patterns by hour of day"""
    hour_counts = {hour: 0 for hour in range(24)}
    
    for track in recent_tracks:
        played_at = track.get('played_at')
        if played_at:
            # Parse ISO format datetime
            from datetime import datetime
            dt = datetime.fromisoformat(played_at.replace('Z', '+00:00'))
            hour = dt.hour
            hour_counts[hour] += 1
    
    return hour_counts

def calculate_average_features(features_list: list) -> Dict[str, float]:
    """Calculate average audio features"""
    if not features_list:
        return {}
    
    feature_keys = ['danceability', 'energy', 'valence', 'tempo', 'acousticness', 
                   'instrumentalness', 'liveness', 'speechiness']
    
    averages = {}
    for key in feature_keys:
        values = [f.get(key, 0) for f in features_list if f.get(key) is not None]
        if values:
            averages[key] = sum(values) / len(values)
        else:
            averages[key] = 0.0
    
    return averages