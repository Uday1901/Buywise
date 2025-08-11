import os
import json
import hashlib
from datetime import datetime, timedelta
from config import Config

class CacheManager:
    def __init__(self):
        self.cache_dir = Config.CACHE_DIR
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def _get_cache_key(self, query, store=None):
        """Generate cache key from query and store"""
        cache_string = f"{query}_{store}" if store else query
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    def _get_cache_path(self, cache_key):
        """Get full path to cache file"""
        return os.path.join(self.cache_dir, f"{cache_key}.json")
    
    def get(self, query, store=None):
        """Get cached data if not expired"""
        cache_key = self._get_cache_key(query, store)
        cache_path = self._get_cache_path(cache_key)
        
        if not os.path.exists(cache_path):
            return None
        
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check if cache is expired
            cached_time = datetime.fromisoformat(data['timestamp'])
            if datetime.now() - cached_time > timedelta(seconds=Config.CACHE_TIMEOUT):
                os.remove(cache_path)
                return None
            
            return data['results']
        except Exception as e:
            print(f"Cache read error: {e}")
            return None
    
    def set(self, query, results, store=None):
        """Cache the results"""
        cache_key = self._get_cache_key(query, store)
        cache_path = self._get_cache_path(cache_key)
        
        cache_data = {
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'store': store,
            'results': results
        }
        
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Cache write error: {e}")
