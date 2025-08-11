from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
from datetime import datetime
import pandas as pd

from config import Config
from scrapers import ScraperManager
from utils.cache import CacheManager

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Initialize managers
scraper_manager = ScraperManager()
cache_manager = CacheManager()

def search_with_cache(query, stores=None):
    """Search with caching support"""
    # Check cache first
    cached_results = cache_manager.get(query)
    if cached_results:
        print(f"Returning cached results for: {query}")
        return cached_results
    
    # Perform fresh search
    if stores:
        # Search specific stores
        all_results = []
        for store in stores:
            scraper = scraper_manager.get_scraper(store)
            if scraper:
                results = scraper.search(query)
                all_results.extend(results)
    else:
        # Search all stores
        all_results = scraper_manager.search_all_stores(query)
    
    # Cache results
    cache_manager.set(query, all_results)
    
    return all_results

@app.route('/')
def home():
    """API information endpoint"""
    return jsonify({
        'name': 'Price Comparison API',
        'version': '1.0',
        'endpoints': [
            '/search?q=product_name',
            '/search?q=product_name&stores=amazon,flipkart',
            '/search?q=product_name&sort=price',
            '/stores',
            '/health'
        ],
        'available_stores': list(scraper_manager.get_all_scrapers().keys())
    })

@app.route('/search', methods=['GET'])
def search():
    """Main search endpoint"""
    query = request.args.get('q', '').strip()
    stores = request.args.get('stores', '').strip()
    sort_by = request.args.get('sort', 'price').strip()
    min_rating = float(request.args.get('min_rating', Config.MIN_RATING))
    limit = int(request.args.get('limit', Config.RESULTS_LIMIT))
    
    if not query:
        return jsonify({
            'error': 'Query parameter "q" is required',
            'example': '/search?q=iphone'
        }), 400
    
    try:
        # Parse stores filter
        store_list = None
        if stores:
            store_list = [s.strip().lower() for s in stores.split(',')]
            # Validate store names
            invalid_stores = [s for s in store_list if s not in scraper_manager.get_all_scrapers()]
            if invalid_stores:
                return jsonify({
                    'error': f'Invalid stores: {invalid_stores}',
                    'available_stores': list(scraper_manager.get_all_scrapers().keys())
                }), 400
        
        # Perform search
        results = search_with_cache(query, store_list)
        
        # Filter by rating
        filtered_results = [r for r in results if r['rating'] >= min_rating]
        
        # Sort results
        if sort_by == 'price':
            filtered_results.sort(key=lambda x: x['price'])
        elif sort_by == 'rating':
            filtered_results.sort(key=lambda x: x['rating'], reverse=True)
        elif sort_by == 'name':
            filtered_results.sort(key=lambda x: x['name'].lower())
        
        # Limit results
        filtered_results = filtered_results[:limit]
        
        # Add metadata
        response = {
            'query': query,
            'total_results': len(filtered_results),
            'search_time': datetime.now().isoformat(),
            'filters': {
                'stores': store_list or 'all',
                'min_rating': min_rating,
                'sort_by': sort_by
            },
            'results': filtered_results
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            'error': f'Search failed: {str(e)}',
            'query': query
        }), 500

@app.route('/stores', methods=['GET'])
def get_stores():
    """Get available stores"""
    stores = {}
    for name, scraper in scraper_manager.get_all_scrapers().items():
        stores[name] = {
            'name': scraper.get_store_name(),
            'status': 'active'
        }
    
    return jsonify({
        'stores': stores,
        'total': len(stores)
    })

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'scrapers': len(scraper_manager.get_all_scrapers())
    })

@app.route('/compare', methods=['GET'])
def compare():
    """Compare specific products across stores"""
    query = request.args.get('q', '').strip()
    
    if not query:
        return jsonify({'error': 'Query parameter required'}), 400
    
    try:
        results = search_with_cache(query)
        
        # Group by store
        comparison = {}
        for result in results:
            store = result['store']
            if store not in comparison:
                comparison[store] = []
            comparison[store].append(result)
        
        # Find best deals
        all_prices = [r['price'] for r in results if r['price'] > 0]
        best_price = min(all_prices) if all_prices else 0
        
        best_deals = [r for r in results if r['price'] == best_price]
        
        return jsonify({
            'query': query,
            'comparison': comparison,
            'best_price': best_price,
            'best_deals': best_deals,
            'total_products': len(results)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("Starting Price Comparison API...")
    print(f"Available stores: {list(scraper_manager.get_all_scrapers().keys())}")
    app.run(debug=Config.DEBUG, host='0.0.0.0', port=5000)

# Add to your main app.py
from intelligent_agent import SmartShoppingAgent
from price_monitoring_agent import PriceMonitoringAgent
import asyncio
import threading

# Initialize agents
shopping_agent = SmartShoppingAgent(api_key="your-openai-api-key")
# Define or import notification_service
from utils.notification_service import NotificationService  # Example import, adjust as needed
notification_service = NotificationService()

price_monitor = PriceMonitoringAgent(scraper_manager, notification_service)

# Start price monitoring in background
def start_price_monitoring():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(price_monitor.monitor_prices())

monitoring_thread = threading.Thread(target=start_price_monitoring, daemon=True)
monitoring_thread.start()

@app.route('/intelligent-search', methods=['POST'])
def intelligent_search():
    """AI-powered product search with natural language understanding"""
    data = request.json
    user_query = data.get('query', '')
    user_preferences = data.get('preferences', {})
    
    try:
        # Process user intent with AI
        intent_analysis = shopping_agent.process_user_intent(user_query, user_preferences)
        
        # Perform enhanced search based on AI analysis
        search_params = {
            'q': intent_analysis.get('search_query', user_query),
            'min_rating': intent_analysis.get('min_rating', 3.0),
            'sort': intent_analysis.get('preferred_sort', 'price')
        }
        
        # Get search results
        results = search_with_cache(search_params['q'])
        
        # AI analysis of deals
        deal_analysis = shopping_agent.analyze_deals(results[:10])
        
        # Generate personalized advice
        user_profile = {
            'budget': intent_analysis.get('budget_range'),
            'priorities': intent_analysis.get('priorities', []),
            'preferences': user_preferences
        }
        
        personalized_advice = shopping_agent.generate_personalized_advice(
            user_profile, results[:5]
        )
        
        return jsonify({
            'intent_analysis': intent_analysis,
            'results': results,
            'ai_analysis': deal_analysis,
            'personalized_advice': personalized_advice,
            'total_results': len(results)
        })
        
    except Exception as e:
        return jsonify({'error': f'AI search failed: {str(e)}'}), 500

@app.route('/add-to-watchlist', methods=['POST'])
def add_to_watchlist():
    """Add product to AI price monitoring"""
    data = request.json
    user_id = data.get('user_id', 'anonymous')
    product_query = data.get('query')
    target_price = float(data.get('target_price'))
    
    if not product_query or not target_price:
        return jsonify({'error': 'Query and target price required'}), 400
    
    try:
        result = asyncio.run(price_monitor.add_to_watchlist(
            user_id, product_query, target_price
        ))
        
        return jsonify({
            'message': result,
            'watchlist_id': f"{user_id}_{hash(product_query)}",
            'monitoring_active': True
        })
        
    except Exception as e:
        return jsonify({'error': f'Watchlist failed: {str(e)}'}), 500

@app.route('/smart-recommendations', methods=['POST'])
def smart_recommendations():
    """Get AI-powered product recommendations"""
    data = request.json
    user_behavior = data.get('user_behavior', {})  # past searches, purchases
    current_query = data.get('query')
    
    try:
        # Analyze user behavior patterns
        recommendation_prompt = f"""
        Based on user's shopping behavior: {user_behavior}
        Current search: {current_query}
        
        Suggest 5 related products they might be interested in.
        Consider complementary items, upgrades, and alternatives.
        """
        
        response = shopping_agent.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a product recommendation expert."},
                {"role": "user", "content": recommendation_prompt}
            ],
            temperature=0.6
        )
        
        # Search for recommended products
        recommendations = []
        suggested_searches = response.choices[0].message.content.split('\n')
        
        for suggestion in suggested_searches[:3]:
            if suggestion.strip():
                results = search_with_cache(suggestion.strip())
                if results:
                    recommendations.extend(results[:2])
        
        return jsonify({
            'recommendations': recommendations,
            'reasoning': response.choices[0].message.content
        })
        
    except Exception as e:
        return jsonify({'error': f'Recommendations failed: {str(e)}'}), 500
