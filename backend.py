"""
Backend logic for Travel Texas AI Agent
Handles API calls, data processing, and business logic
"""

import requests
import json
import time
import tiktoken
import os
from typing import Dict
from dotenv import load_dotenv
from agent_prompt import TEXAS_TOURISM_AGENT_PROMPT, WELCOME_MESSAGE
from cost_engine import CostCalculationEngine
from budget_manager import BudgetManager
from analytics_dashboard import AnalyticsDashboard

# Load environment variables
load_dotenv()


class TravelTexasBackend:
    """Backend service for Travel Texas AI Agent"""
    
    def __init__(self):
        self.config_file = "models_config.json"
        self.models_config = self.load_models_config()
        self.available_models = self.models_config.get("models", {})
        self.default_model = self.models_config.get("default_model", "openai/gpt-4.1-mini")
        self.system_prompt = TEXAS_TOURISM_AGENT_PROMPT
        
        # Initialize cost management system with shared Supabase client
        from supabase_client import SupabaseClient
        shared_supabase = SupabaseClient()
        
        self.cost_engine = CostCalculationEngine()
        self.cost_engine.supabase = shared_supabase
        
        self.budget_manager = BudgetManager()
        self.budget_manager.supabase = shared_supabase
        
        self.analytics_dashboard = AnalyticsDashboard()
        self.analytics_dashboard.cost_engine.supabase = shared_supabase
        self.analytics_dashboard.budget_manager.supabase = shared_supabase
        
    def load_models_config(self):
        """Load models configuration from JSON file"""
        try:
            config_path = os.path.join(os.path.dirname(__file__), self.config_file)
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: {self.config_file} not found. Using default models.")
            return self.get_default_config()
        except json.JSONDecodeError as e:
            print(f"Error parsing {self.config_file}: {e}. Using default models.")
            return self.get_default_config()
    
    def get_default_config(self):
        """Fallback default configuration if config file is not available"""
        return {
            "models": {
                "openai/gpt-4.1-mini": {
                    "name": "GPT-4.1 Mini",
                    "provider": "OpenAI",
                    "emoji": "💨",
                    "description": "Fast, cost-effective model",
                    "pricing": {
                        "input_tokens_per_million": 0.40,
                        "output_tokens_per_million": 1.60
                    },
                    "capabilities": ["fast", "reliable", "general"],
                    "max_tokens": 4000,
                    "available": True
                }
            },
            "default_model": "openai/gpt-4.1-mini"
        }

    def get_available_models(self):
        """Get list of available AI models"""
        return self.available_models

    def get_model_config(self, selected_model):
        """Get configuration for selected model"""
        model_info = self.available_models[selected_model]
        
        return {
            'name': 'Texas Tourism Agent',
            'display_name': model_info['name'],
            'model': selected_model,  # Use the actual model ID
            'emoji': model_info['emoji'],
            'provider': model_info.get('provider', 'Unknown'),
            'description': model_info.get('description', ''),
            'pricing': model_info.get('pricing', {}),
            'capabilities': model_info.get('capabilities', []),
            'color': '#FF6B6B',
            'cta_text': 'Explore Texas Now!',
            'cta_url': 'https://www.traveltexas.com',
            'system_prompt': self.system_prompt
        }
    
    def calculate_cost(self, model_id, input_tokens, output_tokens):
        """Calculate the cost for a given model and token usage"""
        if model_id not in self.available_models:
            return 0.0
        
        model_info = self.available_models[model_id]
        pricing = model_info.get('pricing', {})
        
        input_cost_per_million = pricing.get('input_tokens_per_million', 0)
        output_cost_per_million = pricing.get('output_tokens_per_million', 0)
        
        # Calculate costs
        input_cost = (input_tokens / 1_000_000) * input_cost_per_million
        output_cost = (output_tokens / 1_000_000) * output_cost_per_million
        
        total_cost = input_cost + output_cost
        
        return {
            'input_cost': input_cost,
            'output_cost': output_cost,
            'total_cost': total_cost,
            'input_tokens': input_tokens,
            'output_tokens': output_tokens
        }
    
    def estimate_conversation_cost(self, model_id, estimated_input_tokens=100, estimated_output_tokens=400):
        """Estimate cost for a typical conversation"""
        return self.calculate_cost(model_id, estimated_input_tokens, estimated_output_tokens)
    
    def get_model_comparison(self):
        """Get comparison data for all available models"""
        comparison = []
        for model_id, model_info in self.available_models.items():
            if model_info.get('available', True):
                pricing = model_info.get('pricing', {})
                estimated_cost = self.estimate_conversation_cost(model_id)
                
                comparison.append({
                    'id': model_id,
                    'name': model_info['name'],
                    'provider': model_info.get('provider', 'Unknown'),
                    'emoji': model_info['emoji'],
                    'input_cost_per_million': pricing.get('input_tokens_per_million', 0),
                    'output_cost_per_million': pricing.get('output_tokens_per_million', 0),
                    'estimated_conversation_cost': estimated_cost['total_cost'],
                    'capabilities': model_info.get('capabilities', []),
                    'description': model_info.get('description', '')
                })
        
        # Sort by estimated conversation cost (cheapest first)
        comparison.sort(key=lambda x: x['estimated_conversation_cost'])
        return comparison

    def count_tokens(self, text, model_name="gpt-3.5-turbo"):
        """Estimate token count using tiktoken"""
        try:
            encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
            return len(encoding.encode(text))
        except:
            # Fallback estimation: roughly 4 characters per token
            return len(text) // 4

    def call_openrouter_api_streaming(self, messages, model_config):
        """Call OpenRouter API with streaming - yields content chunks"""
        # Get API key from environment variables
        api_key = os.getenv('OPENROUTER_API_KEY')
        if not api_key:
            raise ValueError("OpenRouter API key not found in environment variables")
        
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "X-Title": "Travel Texas Chat Agent"
        }

        data = {
            "model": model_config['model'],
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 400,
            "stream": True
        }

        try:
            response = requests.post(url, headers=headers, json=data, timeout=30, stream=True)
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        data_str = line_str[6:]  # Remove 'data: ' prefix
                        if data_str.strip() == '[DONE]':
                            break
                        try:
                            data_json = json.loads(data_str)
                            if 'choices' in data_json and len(data_json['choices']) > 0:
                                delta = data_json['choices'][0].get('delta', {})
                                if 'content' in delta:
                                    yield delta['content']  # Stream the content
                        except json.JSONDecodeError:
                            continue
                            
        except requests.exceptions.RequestException as e:
            yield f"API Error: {str(e)}"
        except Exception as e:
            yield f"Error: {str(e)}"

    def get_welcome_message(self):
        """Get the initial welcome message"""
        return WELCOME_MESSAGE

    def validate_api_key(self, api_key):
        """Validate if API key is provided"""
        return bool(api_key and api_key.strip())

    def estimate_token_usage(self, text):
        """Estimate token usage for a given text"""
        total_tokens = self.count_tokens(text)
        return {
            'input_tokens': total_tokens // 2,
            'output_tokens': total_tokens // 2,
            'total_tokens': total_tokens
        }
    
    # Cost Management Methods
    def start_cost_tracking_session(self, model_used: str) -> str:
        """Start a new cost tracking session"""
        return self.cost_engine.start_session(model_used)
    
    def log_user_message(self, message: str, model_used: str) -> Dict:
        """Log a user message and calculate cost"""
        input_tokens = self.count_tokens(message)
        return self.cost_engine.log_message("user", input_tokens, 0, model_used, message)
    
    def log_assistant_message(self, message: str, model_used: str) -> Dict:
        """Log an assistant message and calculate cost"""
        output_tokens = self.count_tokens(message)
        return self.cost_engine.log_message("assistant", 0, output_tokens, model_used, message)
    
    def get_session_summary(self) -> Dict:
        """Get current session cost summary"""
        return self.cost_engine.get_session_summary()
    
    def end_cost_tracking_session(self):
        """End the current cost tracking session"""
        self.cost_engine.end_session()
    
    def get_cost_comparison_table(self):
        """Get cost comparison table data"""
        return self.cost_engine.generate_cost_comparison_table()
    
    def get_budget_status(self, budget_type: str = "daily") -> Dict:
        """Get budget status"""
        return self.budget_manager.get_budget_status(budget_type)
    
    def create_budget(self, budget_type: str, limit_amount: float) -> bool:
        """Create a new budget"""
        if budget_type == "daily":
            return self.budget_manager.create_daily_budget(limit_amount)
        elif budget_type == "monthly":
            return self.budget_manager.create_monthly_budget(limit_amount)
        elif budget_type == "total":
            return self.budget_manager.create_total_budget(limit_amount)
        return False
    
    def get_analytics_data(self, days: int = 30) -> Dict:
        """Get analytics data"""
        return self.cost_engine.get_historical_data(days)
    
    def get_usage_trends_chart(self, days: int = 30):
        """Get usage trends chart"""
        return self.analytics_dashboard.generate_usage_trends_chart(days)
    
    def get_model_usage_pie_chart(self, days: int = 30):
        """Get model usage pie chart"""
        return self.analytics_dashboard.generate_model_usage_pie_chart(days)
    
    def get_budget_status_chart(self):
        """Get budget status chart"""
        return self.analytics_dashboard.generate_budget_status_chart()
    
    def get_cost_efficiency_report(self) -> Dict:
        """Get cost efficiency report"""
        return self.analytics_dashboard.generate_cost_efficiency_report()
    
    def export_analytics_data(self, format: str = "csv") -> str:
        """Export analytics data"""
        return self.analytics_dashboard.export_analytics_data(format)
