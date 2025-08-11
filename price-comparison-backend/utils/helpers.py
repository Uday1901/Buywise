import re
import random
from config import Config

def clean_price(price_text):
    """Extract price from text"""
    if not price_text:
        return 0
    
    # Remove currency symbols and extract numbers
    price_cleaned = re.sub(r'[^\d,.]', '', price_text)
    price_cleaned = price_cleaned.replace(',', '')
    
    try:
        return float(price_cleaned)
    except:
        return 0

def clean_rating(rating_text):
    """Extract rating from text"""
    if not rating_text:
        return 0
    
    # Extract first decimal number
    match = re.search(r'(\d+\.?\d*)', rating_text)
    if match:
        try:
            return float(match.group(1))
        except:
            return 0
    return 0

def get_random_user_agent():
    """Get random user agent"""
    return random.choice(Config.USER_AGENTS)

def clean_text(text):
    """Clean and normalize text"""
    if not text:
        return ""
    return ' '.join(text.strip().split())

def extract_product_id(url):
    """Extract product ID from URL for tracking"""
    if 'amazon' in url:
        match = re.search(r'/dp/([A-Z0-9]{10})', url)
        return match.group(1) if match else None
    elif 'flipkart' in url:
        match = re.search(r'/p/([^?]+)', url)
        return match.group(1) if match else None
    return None
