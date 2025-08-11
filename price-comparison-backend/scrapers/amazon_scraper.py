from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from scrapers.base_scraper import BaseScraper
from utils.helpers import clean_price, clean_rating, clean_text

class AmazonScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.amazon.in"
    
    def get_store_name(self):
        return "Amazon"
    
    def search(self, query):
        """Search Amazon for products"""
        try:
            search_url = f"{self.base_url}/s?k={quote_plus(query)}"
            response = self.make_request(search_url)
            
            if not response:
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            products = []
            
            # Find product containers
            product_containers = soup.find_all('div', {'data-component-type': 's-search-result'})
            
            for container in product_containers[:10]:  # Limit to 10 products
                try:
                    # Product name
                    name_elem = container.find('h2', class_='a-size-mini')
                    if not name_elem:
                        name_elem = container.find('span', class_='a-size-medium')
                    name = clean_text(name_elem.get_text()) if name_elem else "N/A"
                    
                    # Price
                    price_elem = container.find('span', class_='a-price-whole')
                    if not price_elem:
                        price_elem = container.find('span', class_='a-offscreen')
                    price_text = price_elem.get_text() if price_elem else "0"
                    price = clean_price(price_text)
                    
                    # Rating
                    rating_elem = container.find('span', class_='a-icon-alt')
                    rating_text = rating_elem.get_text() if rating_elem else "0"
                    rating = clean_rating(rating_text)
                    
                    # Product URL
                    link_elem = container.find('h2', class_='a-size-mini')
                    if link_elem:
                        link_elem = link_elem.find('a')
                    product_url = self.base_url + link_elem['href'] if link_elem and 'href' in link_elem.attrs else ""
                    
                    # Image
                    img_elem = container.find('img', class_='s-image')
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
                    print(f"Error parsing Amazon product: {e}")
                    continue
            
            return products
            
        except Exception as e:
            print(f"Amazon search error: {e}")
            return []
