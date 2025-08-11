class PriceComparisonAPI {
    constructor() {
        // Replace with your actual API URL
        this.baseURL = 'http://localhost:5000'; // For local development
        // this.baseURL = 'https://your-app-name.onrender.com'; // For production
        this.timeout = 30000; // 30 seconds
    }

    async makeRequest(endpoint, params = {}) {
        const url = new URL(endpoint, this.baseURL);
        
        // Add parameters to URL
        Object.keys(params).forEach(key => {
            if (params[key] !== '' && params[key] !== null && params[key] !== undefined) {
                url.searchParams.append(key, params[key]);
            }
        });

        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.timeout);

        try {
            const response = await fetch(url.toString(), {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
                signal: controller.signal
            });

            clearTimeout(timeoutId);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return data;

        } catch (error) {
            clearTimeout(timeoutId);
            
            if (error.name === 'AbortError') {
                throw new Error('Request timeout - please try again');
            }
            
            throw new Error(`API Error: ${error.message}`);
        }
    }

    async searchProducts(query, options = {}) {
        const params = {
            q: query,
            stores: options.stores || '',
            sort: options.sort || 'price',
            min_rating: options.minRating || 0,
            limit: options.limit || 20
        };

        return await this.makeRequest('/search', params);
    }

    async getStores() {
        return await this.makeRequest('/stores');
    }

    async compareProducts(query) {
        return await this.makeRequest('/compare', { q: query });
    }

    async getHealth() {
        return await this.makeRequest('/health');
    }
}

// Create global API instance
window.priceAPI = new PriceComparisonAPI();
