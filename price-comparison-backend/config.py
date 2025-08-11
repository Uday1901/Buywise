import os
from datetime import timedelta

class Config:
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    DEBUG = True
    
    # Cache settings
    CACHE_TIMEOUT = 1800  # 30 minutes
    CACHE_DIR = 'data/cache'
    
    # Request settings
    REQUEST_TIMEOUT = 10
    MAX_RETRIES = 3
    DELAY_BETWEEN_REQUESTS = 1
    
    # User agents for scraping
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
    ]
    
    # API settings
    RESULTS_LIMIT = 20
    MIN_RATING = 3.0
