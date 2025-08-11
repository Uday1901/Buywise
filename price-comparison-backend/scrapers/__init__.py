from .amazon_scraper import AmazonScraper
from .flipkart_scraper import FlipkartScraper
from .snapdeal_scraper import SnapdealScraper

class ScraperManager:
    def __init__(self):
        self.scrapers = {
            'amazon': AmazonScraper(),
            'flipkart': FlipkartScraper(),
            'snapdeal': SnapdealScraper(),
        }
    
    def get_scraper(self, store_name):
        """Get specific scraper by store name"""
        return self.scrapers.get(store_name.lower())
    
    def get_all_scrapers(self):
        """Get all available scrapers"""
        return self.scrapers
    
    def search_all_stores(self, query):
        """Search across all stores"""
        all_results = []
        
        for store_name, scraper in self.scrapers.items():
            try:
                print(f"Searching {scraper.get_store_name()}...")
                results = scraper.search(query)
                all_results.extend(results)
            except Exception as e:
                print(f"Error searching {store_name}: {e}")
                continue
        
        return all_results
