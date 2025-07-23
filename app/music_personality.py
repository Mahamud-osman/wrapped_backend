from typing import List, Dict, Any
from dataclasses import dataclass
import statistics
from .models import Artist, Track, AudioFeatures

@dataclass
class PersonalityScore:
    category: str
    percentage: float
    description: str
    traits: List[str]

class MusicPersonalityAnalyzer:
    """Analyzes music taste and categorizes into personality types"""
    
    def __init__(self):
        self.genre_weights = {
            # Mainstream/Popular genres
            'pop': {'performative': 0.8, 'pandering': 0.6},
            'top 40': {'performative': 0.9, 'pandering': 0.8},
            'mainstream': {'performative': 0.8, 'pandering': 0.7},
            
            # Experimental/Avant-garde genres
            'experimental': {'avant_garde': 0.9, 'sophisticated': 0.7},
            'noise': {'avant_garde': 0.8, 'sophisticated': 0.6},
            'ambient': {'avant_garde': 0.6, 'sophisticated': 0.8},
            'drone': {'avant_garde': 0.7, 'sophisticated': 0.7},
            'free jazz': {'avant_garde': 0.8, 'sophisticated': 0.9},
            
            # Sophisticated genres
            'classical': {'sophisticated': 0.9, 'avant_garde': 0.3},
            'jazz': {'sophisticated': 0.8, 'explorer': 0.6},
            'baroque': {'sophisticated': 0.9, 'avant_garde': 0.4},
            'opera': {'sophisticated': 0.8, 'performative': 0.4},
            'chamber music': {'sophisticated': 0.9, 'avant_garde': 0.3},
            
            # Explorer genres (diverse/world music)
            'world': {'explorer': 0.8, 'sophisticated': 0.5},
            'afrobeat': {'explorer': 0.7, 'trendsetter': 0.6},
            'k-pop': {'explorer': 0.6, 'trendsetter': 0.8},
            'bossa nova': {'explorer': 0.7, 'sophisticated': 0.6},
            'cumbia': {'explorer': 0.8, 'trendsetter': 0.5},
            
            # Trendsetter genres
            'hyperpop': {'trendsetter': 0.9, 'avant_garde': 0.6},
            'phonk': {'trendsetter': 0.8, 'explorer': 0.5},
            'drill': {'trendsetter': 0.7, 'performative': 0.6},
            'bedroom pop': {'trendsetter': 0.6, 'sophisticated': 0.7},
        }

    def analyze_personality(self, artists: List[Artist], tracks: List[Track], 
                          audio_features: List[AudioFeatures]) -> List[PersonalityScore]:
        """Main analysis function that returns personality breakdown"""
        
        scores = {
            'performative': 0.0,
            'avant_garde': 0.0, 
            'pandering': 0.0,
            'sophisticated': 0.0,
            'explorer': 0.0,
            'trendsetter': 0.0
        }
        
        # Analyze based on different factors
        popularity_scores = self._analyze_popularity(artists, tracks)
        genre_scores = self._analyze_genres(artists)
        audio_scores = self._analyze_audio_features(audio_features)
        diversity_scores = self._analyze_diversity(artists, tracks)
        
        # Combine scores with weights
        for category in scores.keys():
            scores[category] = (
                popularity_scores.get(category, 0) * 0.3 +
                genre_scores.get(category, 0) * 0.3 +
                audio_scores.get(category, 0) * 0.25 +
                diversity_scores.get(category, 0) * 0.15
            )
        
        # Normalize to percentages
        total = sum(scores.values()) or 1
        normalized_scores = {k: (v / total) * 100 for k, v in scores.items()}
        
        # Create personality score objects
        personality_types = self._get_personality_descriptions()
        results = []
        
        for category, percentage in normalized_scores.items():
            if percentage > 5:  # Only include significant categories
                results.append(PersonalityScore(
                    category=category,
                    percentage=round(percentage, 1),
                    description=personality_types[category]['description'],
                    traits=personality_types[category]['traits']
                ))
        
        # Sort by percentage
        results.sort(key=lambda x: x.percentage, reverse=True)
        return results

    def _analyze_popularity(self, artists: List[Artist], tracks: List[Track]) -> Dict[str, float]:
        """Analyze based on popularity scores"""
        artist_popularities = [a.popularity for a in artists if a.popularity]
        track_popularities = [t.popularity for t in tracks if t.popularity]
        
        if not artist_popularities and not track_popularities:
            return {}
        
        avg_popularity = statistics.mean(artist_popularities + track_popularities)
        
        scores = {}
        if avg_popularity >= 70:
            scores['performative'] = 0.8
            scores['pandering'] = 0.6
        elif avg_popularity <= 30:
            scores['avant_garde'] = 0.7
            scores['sophisticated'] = 0.5
        else:
            scores['explorer'] = 0.6
            
        return scores

    def _analyze_genres(self, artists: List[Artist]) -> Dict[str, float]:
        """Analyze based on genre preferences"""
        all_genres = []
        for artist in artists:
            all_genres.extend(artist.genres)
        
        if not all_genres:
            return {}
        
        scores = {category: 0.0 for category in ['performative', 'avant_garde', 'pandering', 
                                                'sophisticated', 'explorer', 'trendsetter']}
        
        for genre in all_genres:
            genre_lower = genre.lower()
            for genre_key, weights in self.genre_weights.items():
                if genre_key in genre_lower or any(word in genre_lower for word in genre_key.split()):
                    for category, weight in weights.items():
                        scores[category] += weight
        
        # Normalize by number of genres
        if all_genres:
            for category in scores:
                scores[category] = scores[category] / len(all_genres)
        
        return scores

    def _analyze_audio_features(self, audio_features: List[AudioFeatures]) -> Dict[str, float]:
        """Analyze based on audio characteristics"""
        if not audio_features:
            return {}
        
        # Calculate averages
        avg_energy = statistics.mean([f.energy for f in audio_features])
        avg_danceability = statistics.mean([f.danceability for f in audio_features])
        avg_valence = statistics.mean([f.valence for f in audio_features])
        avg_acousticness = statistics.mean([f.acousticness for f in audio_features])
        avg_instrumentalness = statistics.mean([f.instrumentalness for f in audio_features])
        
        scores = {}
        
        # High energy + danceability = pandering/performative
        if avg_energy > 0.7 and avg_danceability > 0.7:
            scores['pandering'] = 0.7
            scores['performative'] = 0.5
        
        # High acousticness + low energy = sophisticated
        if avg_acousticness > 0.6 and avg_energy < 0.4:
            scores['sophisticated'] = 0.8
        
        # High instrumentalness = avant-garde
        if avg_instrumentalness > 0.5:
            scores['avant_garde'] = 0.6
        
        # Very low or very high valence = avant-garde
        if avg_valence < 0.3 or avg_valence > 0.9:
            scores['avant_garde'] = scores.get('avant_garde', 0) + 0.4
        
        return scores

    def _analyze_diversity(self, artists: List[Artist], tracks: List[Track]) -> Dict[str, float]:
        """Analyze musical diversity"""
        all_genres = []
        for artist in artists:
            all_genres.extend(artist.genres)
        
        unique_genres = len(set(all_genres))
        total_genres = len(all_genres) or 1
        
        diversity_ratio = unique_genres / total_genres
        
        scores = {}
        if diversity_ratio > 0.7:
            scores['explorer'] = 0.8
            scores['trendsetter'] = 0.5
        elif diversity_ratio < 0.3:
            scores['pandering'] = 0.6
        
        return scores

    def _get_personality_descriptions(self) -> Dict[str, Dict[str, Any]]:
        """Get descriptions for each personality type"""
        return {
            'performative': {
                'description': 'You love music that makes a statement and gets attention',
                'traits': ['Enjoys popular hits', 'Likes energetic music', 'Values mainstream appeal', 'Appreciates polished production']
            },
            'avant_garde': {
                'description': 'You seek out experimental and boundary-pushing sounds',
                'traits': ['Appreciates complexity', 'Enjoys unusual sounds', 'Values artistic innovation', 'Open to challenging music']
            },
            'pandering': {
                'description': 'You enjoy feel-good, accessible music that hits the right spots',
                'traits': ['Prefers catchy melodies', 'Likes danceable beats', 'Values emotional appeal', 'Enjoys familiar structures']
            },
            'sophisticated': {
                'description': 'You appreciate nuanced, intellectually engaging music',
                'traits': ['Values musical complexity', 'Enjoys acoustic elements', 'Appreciates craftsmanship', 'Prefers depth over intensity']
            },
            'explorer': {
                'description': 'You love discovering diverse sounds from around the world',
                'traits': ['Seeks musical diversity', 'Enjoys world music', 'Values cultural exploration', 'Open to new experiences']
            },
            'trendsetter': {
                'description': 'You stay ahead of the curve with emerging sounds and artists',
                'traits': ['Discovers new genres early', 'Values innovation', 'Enjoys cutting-edge production', 'Influences others\' taste']
            }
        }