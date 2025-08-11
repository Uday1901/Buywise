# price_monitoring_agent.py
import asyncio
from datetime import datetime, timedelta
from typing import Dict
import smtplib
from email.mime.text import MIMEText

class PriceMonitoringAgent:
    def __init__(self, scraper_manager, notification_service):
        self.scraper_manager = scraper_manager
        self.notification_service = notification_service
        self.watchlist = {}  # product_id: {user_id, target_price, current_price, ...}
        self.monitoring = False
    
    async def add_to_watchlist(self, user_id: str, product_query: str, target_price: float):
        """Add product to price monitoring watchlist"""
        product_id = f"{user_id}_{hash(product_query)}"
        
        # Get current price
        current_results = self.scraper_manager.search_all_stores(product_query)
        if current_results:
            current_price = min([p['price'] for p in current_results if p['price'] > 0])
            best_deal = min(current_results, key=lambda x: x['price'] if x['price'] > 0 else float('inf'))
            
            self.watchlist[product_id] = {
                'user_id': user_id,
                'query': product_query,
                'target_price': target_price,
                'current_price': current_price,
                'best_deal': best_deal,
                'created_at': datetime.now(),
                'last_checked': datetime.now()
            }
            
            return f"Added to watchlist! Current best price: ₹{current_price}"
        return "Unable to find product for monitoring"
    
    async def monitor_prices(self):
        """Continuously monitor prices for watchlisted items"""
        self.monitoring = True
        
        while self.monitoring:
            for product_id, watch_item in self.watchlist.items():
                try:
                    # Check if it's time to update (every 2 hours)
                    if datetime.now() - watch_item['last_checked'] > timedelta(hours=2):
                        await self.check_price_change(product_id, watch_item)
                        await asyncio.sleep(5)  # Rate limiting
                        
                except Exception as e:
                    print(f"Error monitoring {product_id}: {e}")
            
            # Wait 30 minutes before next monitoring cycle
            await asyncio.sleep(1800)
    
    async def check_price_change(self, product_id: str, watch_item: Dict):
        """Check for price changes and notify if target reached"""
        results = self.scraper_manager.search_all_stores(watch_item['query'])
        
        if results:
            current_best_price = min([p['price'] for p in results if p['price'] > 0])
            current_best_deal = min(results, key=lambda x: x['price'] if x['price'] > 0 else float('inf'))
            
            # Update watch item
            price_dropped = current_best_price < watch_item['current_price']
            target_reached = current_best_price <= watch_item['target_price']
            
            watch_item['current_price'] = current_best_price
            watch_item['best_deal'] = current_best_deal
            watch_item['last_checked'] = datetime.now()
            
            # Send notifications
            if target_reached:
                await self.send_target_reached_notification(watch_item)
            elif price_dropped:
                await self.send_price_drop_notification(watch_item, current_best_price)
    
    async def send_target_reached_notification(self, watch_item: Dict):
        """Send notification when target price is reached"""
        message = f"""
        🎯 TARGET PRICE REACHED!
        
        Product: {watch_item['query']}
        Your Target: ₹{watch_item['target_price']}
        Current Best Price: ₹{watch_item['current_price']}
        
        Store: {watch_item['best_deal']['store']}
        Product: {watch_item['best_deal']['name']}
        Rating: {watch_item['best_deal']['rating']}⭐
        
        Buy now: {watch_item['best_deal']['url']}
        """
        
        await self.notification_service.send_notification(
            watch_item['user_id'], 
            "Price Alert: Target Reached!", 
            message
        )
