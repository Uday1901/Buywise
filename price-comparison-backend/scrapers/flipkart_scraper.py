from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from scrapers.base_scraper import BaseScraper
from utils.helpers import clean_price, clean_rating, clean_text

class FlipkartScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.flipkart.com"
    
    def get_store_name(self):
        return "Flipkart"
    
    def search(self, query):
        """Search Flipkart for products"""
        try:
            search_url = f"{self.base_url}/search?q={quote_plus(query)}"
            response = self.make_request(search_url)
            
            if not response:
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            products = []
            
            # Find product containers (Flipkart uses different selectors)
            product_containers = soup.find_all('div', class_='_1AtVbE')
            if not product_containers:
                product_containers = soup.find_all('div', class_='_13oc-S')
            
            for container in product_containers[:10]:
                try:
                    # Product name
                    name_elem = container.find('div', class_='_4rR01T')
                    if not name_elem:
                        name_elem = container.find('a', class_='IRpwTa')
                    name = clean_text(name_elem.get_text()) if name_elem else "N/A"
                    
                    # Price
                    price_elem = container.find('div', class_='_30jeq3')
                    if not price_elem:
                        price_elem = container.find('div', class_='_1_WHN1')
                    price_text = price_elem.get_text() if price_elem else "0"
                    price = clean_price(price_text)
                    
                    # Rating
                    rating_elem = container.find('div', class_='_3LWZlK')
                    rating_text = rating_elem.get_text() if rating_elem else "0"
                    rating = clean_rating(rating_text)
                    
                    # Product URL
                    link_elem = container.find('a', class_='_1fQZEK')
                    if not link_elem:
                        link_elem = container.find('a')
                    product_url = self.base_url + link_elem['href'] if link_elem and 'href' in link_elem.attrs else ""
                    
                    # Image
                    img_elem = container.find('img', class_='_396cs4')
                    image_url = img_elem['src'] if img_elem and 'src' in img_elem.attrs else ""
                    
                    if name != "N/A" and price > 0:
                        products.append({
                            'name': name,
                            'price': price,
                            'rating': rating,
                            'url': product_url,
                            'image': image_url,
                            'store': self.get_store_name(),
                            'currency': 'INR'
                        })
                        
                except Exception as e:
                    print(f"Error parsing Flipkart product: {e}")
                    continue
            
            return products
            
        except Exception as e:
            print(f"Flipkart search error: {e}")
            return []
