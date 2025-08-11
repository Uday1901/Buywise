# Add to your backend: intelligent_agent.py
import openai
from typing import Dict, List
import json

class SmartShoppingAgent:
    def __init__(self, api_key):
        self.client = openai.OpenAI(api_key=api_key)
        self.conversation_history = []
    
    def process_user_intent(self, user_query: str, user_preferences: Dict = None) -> Dict:
        """Process natural language queries and extract shopping intent"""
        
        system_prompt = """
        You are a smart shopping assistant that helps users find the best products.
        Analyze the user's query and extract:
        1. Product category/type
        2. Budget range (if mentioned)
        3. Specific features or requirements
        4. Urgency level
        5. Quality vs Price preference
        
        Return a structured JSON response with search parameters and personalized advice.
        """
        
        user_context = f"""
        User Query: {user_query}
        User Preferences: {user_preferences or 'None provided'}
        
        Please provide a detailed analysis and shopping recommendations.
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_context}
            ],
            temperature=0.7
        )
        
        try:
            return json.loads(response.choices[0].message.content)
        except:
            return {"search_query": user_query, "category": "general"}
    
    def analyze_deals(self, products: List[Dict]) -> Dict:
        """Analyze products and provide intelligent recommendations"""
        
        analysis_prompt = f"""
        Analyze these products and provide:
        1. Best overall deal
        2. Best value for money
        3. Premium option
        4. Budget-friendly choice
        5. Potential concerns or red flags
        
        Products: {json.dumps(products, indent=2)}
        
        Provide detailed reasoning for each recommendation.
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert product analyst."},
                {"role": "user", "content": analysis_prompt}
            ],
            temperature=0.3
        )
        
        return {"analysis": response.choices[0].message.content}
    
    def generate_personalized_advice(self, user_profile: Dict, products: List[Dict]) -> str:
        """Generate personalized shopping advice"""
        
        advice_prompt = f"""
        Based on this user profile: {user_profile}
        And these products: {json.dumps(products[:3], indent=2)}
        
        Provide personalized shopping advice considering:
        - User's budget and preferences
        - Product quality and reviews
        - Best timing for purchase
        - Alternative suggestions
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a personal shopping advisor."},
                {"role": "user", "content": advice_prompt}
            ],
            temperature=0.7
        )
        
        return response.choices[0].message.content
