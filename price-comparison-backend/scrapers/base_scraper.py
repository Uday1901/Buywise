import requests
import time
from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
from utils.helpers import get_random_user_agent
from config import Config

class BaseScraper(ABC):
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': get_random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
    
    def make_request(self, url, max_retries=None):
        """Make HTTP request with retry logic"""
        max_retries = max_retries or Config.MAX_RETRIES
        
        for attempt in range(max_retries):
            try:
                response = self.session.get(
                    url, 
                    timeout=Config.REQUEST_TIMEOUT,
                    headers={'User-Agent': get_random_user_agent()}
                )
                response.raise_for_status()
                return response
                
            except requests.RequestException as e:
                print(f"Request failed (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(Config.DELAY_BETWEEN_REQUESTS * (attempt + 1))
                else:
                    raise
        
        return None
    
    @abstractmethod
    def search(self, query):
        """Search for products - must be implemented by subclasses"""
        pass
    
    @abstractmethod
    def get_store_name(self):
        """Return store name"""
        pass
