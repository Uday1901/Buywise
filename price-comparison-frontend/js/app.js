class PriceComparisonApp {
    constructor() {
        this.currentResults = [];
        this.currentQuery = '';
        this.isLoading = false;
        this.currentPage = 1;
        this.resultsPerPage = 10;

        this.initializeApp();
        this.bindEvents();
    }

    initializeApp() {
        // Check API health
        this.checkAPIHealth();
        
        // Load popular searches
        this.loadPopularSearches();
        
        // Set focus to search input
        document.getElementById('searchInput').focus();
    }

    async checkAPIHealth() {
        try {
            await window.priceAPI.getHealth();
            console.log('API is healthy');
        } catch (error) {
            console.warn('API health check failed:', error);
            this.showError('API connection issue. Some features may not work properly.');
        }
    }

    bindEvents() {
        // Search functionality
        document.getElementById('searchBtn').addEventListener('click', () => this.handleSearch());
        document.getElementById('searchInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.handleSearch();
        });

        // Clear search
        document.getElementById('clearSearch').addEventListener('click', () => this.clearSearch());

        // Search input changes
        document.getElementById('searchInput').addEventListener('input', (e) => {
            const clearBtn = document.getElementById('clearSearch');
            clearBtn.style.display = e.target.value ? 'block' : 'none';
        });

        // Popular search tags
        document.querySelectorAll('.tag-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const query = e.target.dataset.search;
                document.getElementById('searchInput').value = query;
                this.handleSearch();
            });
        });

        // Load more results
        document.getElementById('loadMoreBtn').addEventListener('click', () => this.loadMoreResults());

        // Filter changes
        document.getElementById('storeFilter').addEventListener('change', () => this.applyFilters());
        document.getElementById('sortFilter').addEventListener('change', () => this.applyFilters());
        document.getElementById('ratingFilter').addEventListener('change', () => this.applyFilters());

        // Smooth scrolling for navigation
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', (e) => {
                e.preventDefault();
                const target = document.querySelector(anchor.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth' });
                }
            });
        });
    }

    async handleSearch() {
        const query = document.getElementById('searchInput').value.trim();
        
        if (!query) {
            this.showError('Please enter a product name to search');
            return;
        }

        if (this.isLoading) return;

        this.currentQuery = query;
        this.currentPage = 1;
        this.showLoadingState();

        try {
            const options = this.getSearchOptions();
            const response = await window.priceAPI.searchProducts(query, options);
            
            this.currentResults = response.results || [];
            this.displayResults(response);
            this.scrollToResults();
            
        } catch (error) {
            this.showError(`Search failed: ${error.message}`);
        } finally {
            this.hideLoadingState();
        }
    }

    getSearchOptions() {
        return {
            stores: document.getElementById('storeFilter').value,
            sort: document.getElementById('sortFilter').value,
            minRating: parseFloat(document.getElementById('ratingFilter').value),
            limit: 50 // Get more results for client-side pagination
        };
    }

    async applyFilters() {
        if (!this.currentQuery) return;
        
        this.showLoadingState();
        
        try {
            const options = this.getSearchOptions();
            const response = await window.priceAPI.searchProducts(this.currentQuery, options);
            
            this.currentResults = response.results || [];
            this.currentPage = 1;
            this.displayResults(response);
            
        } catch (error) {
            this.showError(`Filter failed: ${error.message}`);
        } finally {
            this.hideLoadingState();
        }
    }

    displayResults(response) {
        const resultsSection = document.getElementById('results');
        const resultsTitle = document.getElementById('resultsTitle');
        const resultsCount = document.getElementById('resultsCount');
        const searchTime = document.getElementById('searchTime');
        const productsGrid = document.getElementById('productsGrid');
        const bestDealAlert = document.getElementById('bestDealAlert');

        // Update results info
        resultsTitle.textContent = `Results for "${this.currentQuery}"`;
        resultsCount.textContent = `${response.total_results || 0} products found`;
        searchTime.textContent = response.search_time ? 
            `Search completed at ${new Date(response.search_time).toLocaleTimeString()}` : '';

        // Show best deal alert
        if (this.currentResults.length > 0) {
            const bestPrice = Math.min(...this.currentResults.map(p => p.price));
            const bestDeals = this.currentResults.filter(p => p.price === bestPrice);
            
            if (bestDeals.length > 0) {
                bestDealAlert.style.display = 'flex';
            }
        }

        // Display products
        this.renderProducts();

        // Show results section
        resultsSection.style.display = 'block';
    }

    renderProducts() {
        const productsGrid = document.getElementById('productsGrid');
        const startIndex = 0;
        const endIndex = this.currentPage * this.resultsPerPage;
        const productsToShow = this.currentResults.slice(startIndex, endIndex);

        if (productsToShow.length === 0) {
            productsGrid.innerHTML = `
                <div class="no-results">
                    <i class="fas fa-search" style="font-size: 48px; color: #ccc; margin-bottom: 1rem;"></i>
                    <h3>No products found</h3>
                    <p>Try different keywords or adjust your filters</p>
                </div>
            `;
            return;
        }

        // Find best price for highlighting
        const bestPrice = Math.min(...this.currentResults.map(p => p.price));

        productsGrid.innerHTML = productsToShow.map(product => this.createProductCard(product, product.price === bestPrice)).join('');

        // Show/hide load more button
        const loadMoreBtn = document.getElementById('loadMoreBtn');
        loadMoreBtn.style.display = endIndex < this.currentResults.length ? 'block' : 'none';
    }

    createProductCard(product, isBestDeal = false) {
        const stars = this.generateStars(product.rating);
        const storeBadgeClass = product.store.toLowerCase().replace(/\s+/g, '');
        
        return `
            <div class="product-card ${isBestDeal ? 'best-deal' : ''}">
                <div class="product-header">
                    <span class="store-badge ${storeBadgeClass}">${product.store}</span>
                </div>
                
                <h4 class="product-name" title="${product.name}">${product.name}</h4>
                
                <div class="product-price">₹${this.formatPrice(product.price)}</div>
                
                <div class="product-rating">
                    <span class="rating-stars">${stars}</span>
                    <span class="rating-value">${product.rating || 'No rating'}</span>
                </div>
                
                <div class="product-actions">
                    <a href="${product.url}" target="_blank" class="btn btn-primary">
                        <i class="fas fa-external-link-alt"></i>
                        View Deal
                    </a>
                    <button class="btn btn-outline" onclick="app.compareProduct('${product.name}')">
                        <i class="fas fa-chart-bar"></i>
                        Compare
                    </button>
                </div>
            </div>
        `;
    }

    generateStars(rating) {
        if (!rating) return '<span class="no-rating">No rating</span>';
        
        const fullStars = Math.floor(rating);
        const hasHalfStar = rating % 1 !== 0;
        const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0);
        
        let stars = '';
        
        // Full stars
        for (let i = 0; i < fullStars; i++) {
            stars += '<i class="fas fa-star"></i>';
        }
        
        // Half star
        if (hasHalfStar) {
            stars += '<i class="fas fa-star-half-alt"></i>';
        }
        
        // Empty stars
        for (let i = 0; i < emptyStars; i++) {
            stars += '<i class="far fa-star"></i>';
        }
        
        return stars;
    }

    formatPrice(price) {
        return new Intl.NumberFormat('en-IN').format(price);
    }

    loadMoreResults() {
        this.currentPage++;
        this.renderProducts();
    }

    async compareProduct(productName) {
        try {
            this.showLoadingState();
            const response = await window.priceAPI.compareProducts(productName);
            this.showComparisonModal(response);
        } catch (error) {
            this.showError(`Comparison failed: ${error.message}`);
        } finally {
            this.hideLoadingState();
        }
    }

    showComparisonModal(comparison) {
        // Create and show comparison modal
        const modal = document.createElement('div');
        modal.className = 'comparison-modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Price Comparison: ${comparison.query}</h3>
                    <button class="close-modal">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="comparison-summary">
                        <div class="best-price">
                            <h4>Best Price: ₹${this.formatPrice(comparison.best_price)}</h4>
                            <p>${comparison.best_deals.length} store(s) offering this price</p>
                        </div>
                    </div>
                    <div class="comparison-grid">
                        ${Object.entries(comparison.comparison).map(([store, products]) => `
                            <div class="store-comparison">
                                <h5>${store}</h5>
                                ${products.slice(0, 3).map(product => `
                                    <div class="comparison-item">
                                        <span class="comparison-price">₹${this.formatPrice(product.price)}</span>
                                        <span class="comparison-rating">${product.rating}⭐</span>
                                        <a href="${product.url}" target="_blank">View</a>
                                    </div>
                                `).join('')}
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        // Close modal events
        modal.querySelector('.close-modal').addEventListener('click', () => {
            document.body.removeChild(modal);
        });

        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                document.body.removeChild(modal);
            }
        });
    }

    clearSearch() {
        document.getElementById('searchInput').value = '';
        document.getElementById('clearSearch').style.display = 'none';
        document.getElementById('results').style.display = 'none';
        document.getElementById('searchInput').focus();
    }

    scrollToResults() {
        setTimeout(() => {
            document.getElementById('results').scrollIntoView({ 
                behavior: 'smooth' 
            });
        }, 100);
    }

    showLoadingState() {
        this.isLoading = true;
        const searchBtn = document.getElementById('searchBtn');
        const loadingOverlay = document.getElementById('loadingOverlay');
        
        searchBtn.disabled = true;
        searchBtn.querySelector('.btn-text').style.display = 'none';
        searchBtn.querySelector('.loading-spinner').style.display = 'block';
        
        loadingOverlay.style.display = 'flex';
    }

    hideLoadingState() {
        this.isLoading = false;
        const searchBtn = document.getElementById('searchBtn');
        const loadingOverlay = document.getElementById('loadingOverlay');
        
        searchBtn.disabled = false;
        searchBtn.querySelector('.btn-text').style.display = 'block';
        searchBtn.querySelector('.loading-spinner').style.display = 'none';
        
        loadingOverlay.style.display = 'none';
    }

    showError(message) {
        // Create toast notification
        const toast = document.createElement('div');
        toast.className = 'error-toast';
        toast.innerHTML = `
            <div class="toast-content">
                <i class="fas fa-exclamation-circle"></i>
                <span>${message}</span>
            </div>
        `;

        document.body.appendChild(toast);

        // Auto remove after 5 seconds
        setTimeout(() => {
            if (document.body.contains(toast)) {
                document.body.removeChild(toast);
            }
        }, 5000);

        // Click to dismiss
        toast.addEventListener('click', () => {
            if (document.body.contains(toast)) {
                document.body.removeChild(toast);
            }
        });
    }

    loadPopularSearches() {
        // This could load from an API in the future
        console.log('Popular searches loaded');
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new PriceComparisonApp();
});

// Add to your app.js
class AgenticShoppingAssistant {
    constructor() {
        this.conversationHistory = [];
        this.userPreferences = this.loadUserPreferences();
        this.watchlist = [];
    }
    
    async intelligentSearch(query) {
        const searchData = {
            query: query,
            preferences: this.userPreferences,
            conversation_history: this.conversationHistory
        };
        
        try {
            const response = await fetch(`${API_URL}/intelligent-search`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(searchData)
            });
            
            const data = await response.json();
            
            // Display AI insights
            this.displayAIInsights(data);
            
            return data;
            
        } catch (error) {
            console.error('Intelligent search failed:', error);
            throw error;
        }
    }
    
    displayAIInsights(data) {
        const insightsContainer = document.getElementById('aiInsights');
        
        insightsContainer.innerHTML = `
            <div class="ai-insights-panel">
                <div class="ai-analysis">
                    <h4><i class="fas fa-robot"></i> AI Shopping Assistant</h4>
                    <div class="intent-analysis">
                        <p><strong>Understanding your needs:</strong></p>
                        <p>${data.intent_analysis.analysis || 'Analyzing your search...'}</p>
                    </div>
                    
                    <div class="personalized-advice">
                        <h5><i class="fas fa-lightbulb"></i> Personalized Advice</h5>
                        <div class="advice-content">
                            ${this.formatAdvice(data.personalized_advice)}
                        </div>
                    </div>
                    
                    <div class="deal-analysis">
                        <h5><i class="fas fa-chart-line"></i> Deal Analysis</h5>
                        <div class="analysis-content">
                            ${data.ai_analysis.analysis}
                        </div>
                    </div>
                </div>
                
                <div class="ai-actions">
                    <button class="btn btn-primary" onclick="agenticAssistant.addToWatchlist('${data.intent_analysis.search_query}')">
                        <i class="fas fa-bell"></i> Monitor Price
                    </button>
                    <button class="btn btn-outline" onclick="agenticAssistant.getSmartRecommendations()">
                        <i class="fas fa-magic"></i> Smart Suggestions
                    </button>
                </div>
            </div>
        `;
    }
    
    async addToWatchlist(query) {
        const targetPrice = prompt(`Enter your target price for "${query}":`);
        if (!targetPrice) return;
        
        try {
            const response = await fetch(`${API_URL}/add-to-watchlist`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: this.getUserId(),
                    query: query,
                    target_price: parseFloat(targetPrice)
                })
            });
            
            const data = await response.json();
            
            this.showNotification('success', `Added to watchlist! ${data.message}`);
            this.watchlist.push({ query, target_price: targetPrice });
            
        } catch (error) {
            this.showNotification('error', 'Failed to add to watchlist');
        }
    }
    
    async getSmartRecommendations() {
        try {
            const response = await fetch(`${API_URL}/smart-recommendations`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_behavior: this.getUserBehavior(),
                    query: this.currentQuery
                })
            });
            
            const data = await response.json();
            this.displaySmartRecommendations(data);
            
        } catch (error) {
            console.error('Smart recommendations failed:', error);
        }
    }
    
    displaySmartRecommendations(data) {
        const modal = document.createElement('div');
        modal.className = 'recommendations-modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3><i class="fas fa-robot"></i> AI Recommendations</h3>
                    <button class="close-modal">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="ai-reasoning">
                        <h4>Why we recommend these:</h4>
                        <p>${data.reasoning}</p>
                    </div>
                    <div class="recommendations-grid">
                        ${data.recommendations.map(product => `
                            <div class="recommendation-card">
                                <h5>${product.name}</h5>
                                <div class="rec-price">₹${this.formatPrice(product.price)}</div>
                                <div class="rec-rating">${product.rating}⭐</div>
                                <div class="rec-store">${product.store}</div>
                                <button class="btn btn-sm btn-primary" onclick="window.open('${product.url}', '_blank')">
                                    View Product
                                </button>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        modal.querySelector('.close-modal').addEventListener('click', () => {
            document.body.removeChild(modal);
        });
    }
    
    // Voice search capability
    startVoiceSearch() {
        if ('webkitSpeechRecognition' in window) {
            const recognition = new webkitSpeechRecognition();
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.lang = 'en-IN';
            
            recognition.onstart = () => {
                document.getElementById('voiceBtn').innerHTML = '<i class="fas fa-microphone-slash"></i> Listening...';
            };
            
            recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                document.getElementById('searchInput').value = transcript;
                this.intelligentSearch(transcript);
            };
            
            recognition.onerror = () => {
                this.showNotification('error', 'Voice recognition failed');
            };
            
            recognition.onend = () => {
                document.getElementById('voiceBtn').innerHTML = '<i class="fas fa-microphone"></i> Voice Search';
            };
            
            recognition.start();
        }
    }
    
    formatAdvice(advice) {
        return advice.split('\n').map(line => `<p>${line}</p>`).join('');
    }
    
    getUserId() {
        return localStorage.getItem('userId') || 'anonymous_' + Date.now();
    }
    
    getUserBehavior() {
        return {
            search_history: JSON.parse(localStorage.getItem('searchHistory') || '[]'),
            preferences: this.userPreferences,
            watchlist: this.watchlist
        };
    }
    
    loadUserPreferences() {
        return JSON.parse(localStorage.getItem('userPreferences') || '{}');
    }
    
    showNotification(type, message) {
        // Implementation for showing notifications
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        document.body.appendChild(notification);
        
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 3000);
    }
}

// Initialize agentic assistant
const agenticAssistant = new AgenticShoppingAssistant();
