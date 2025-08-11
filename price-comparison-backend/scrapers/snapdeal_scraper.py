from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from scrapers.base_scraper import BaseScraper
from utils.helpers import clean_price, clean_rating, clean_text

class SnapdealScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.snapdeal.com"
    
    def get_store_name(self):
        return "Snapdeal"
    
    def search(self, query):
        """Search Snapdeal for products"""
        try:
            search_url = f"{self.base_url}/search?keyword={quote_plus(query)}"
            response = self.make_request(search_url)
            
            if not response:
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            products = []
            
            # Find product containers
            product_containers = soup.find_all('div', class_='product-tuple-listing')
            
            for container in product_containers[:10]:
                try:
                    # Product name
                    name_elem = container.find('p', class_='product-title')
                    name = clean_text(name_elem.get_text()) if name_elem else "N/A"
                    
                    # Price
                    price_elem = container.find('span', class_='lfloat product-price')
                    if not price_elem:
                        price_elem = container.find('span', class_='product-price')
                    price_text = price_elem.get_text() if price_elem else "0"
                    price = clean_price(price_text)
                    
                    # Rating
                    rating_elem = container.find('div', class_='filled-stars')
                    rating = 0
                    if rating_elem:
                        style = rating_elem.get('style', '')
                        if 'width:' in style:
                            width = style.split('width:')[1].split('%')[0].strip()
                            rating = round(float(width) / 20, 1) if width.isdigit() else 0
                    
                    # Product URL
                    link_elem = container.find('a', class_='dp-widget-link')
                    product_url = link_elem['href'] if link_elem and 'href' in link_elem.attrs else ""
                    
                    # Image
                    img_elem = container.find('img', class_='product-image')
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
                    print(f"Error parsing Snapdeal product: {e}")
                    continue
            
            return products
            
        except Exception as e:
            print(f"Snapdeal search error: {e}")
            return []
