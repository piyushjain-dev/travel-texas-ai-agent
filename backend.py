"""
Backend logic for Travel Texas AI Agent
Handles API calls, data processing, and business logic
"""

import requests
import json
import time
import tiktoken


class TravelTexasBackend:
    """Backend service for Travel Texas AI Agent"""
    
    def __init__(self):
        self.available_models = {
            'claude-3.5-sonnet': {
                'name': 'Claude 3.5 Sonnet',
                'model': 'anthropic/claude-3.5-sonnet',
                'emoji': '🤠'
            },
            'claude-3-opus': {
                'name': 'Claude 3 Opus',
                'model': 'anthropic/claude-3-opus',
                'emoji': '🧠'
            },
            'claude-3-haiku': {
                'name': 'Claude 3 Haiku',
                'model': 'anthropic/claude-3-haiku',
                'emoji': '⚡'
            },
            'gpt-4o': {
                'name': 'GPT-4o',
                'model': 'openai/gpt-4o',
                'emoji': '🚀'
            },
            'gpt-4o-mini': {
                'name': 'GPT-4o Mini',
                'model': 'openai/gpt-4o-mini',
                'emoji': '💨'
            },
            'llama-3.1-405b': {
                'name': 'Llama 3.1 405B',
                'model': 'meta-llama/llama-3.1-405b-instruct',
                'emoji': '🦙'
            }
        }
        
        self.system_prompt = """You are a persuasive Texas Tourism advertisement agent. Your goal is to SELL Texas as an amazing travel destination and get visitors to book NOW. You should:
- Create excitement and urgency about Texas experiences
- Mention specific deals, packages, and limited-time offers
- Use compelling descriptions of adventures, food, culture, and attractions
- Include social proof and testimonials
- Always end with clear calls-to-action to visit traveltexas.com or book experiences
- Keep responses conversational but sales-focused
Sound like an enthusiastic travel agent who makes Texas irresistible!"""

    def get_available_models(self):
        """Get list of available AI models"""
        return self.available_models

    def get_model_config(self, selected_model):
        """Get configuration for selected model"""
        model_info = self.available_models[selected_model]
        
        return {
            'name': 'Texas Tourism Agent',
            'display_name': model_info['name'],
            'model': model_info['model'],
            'emoji': model_info['emoji'],
            'color': '#FF6B6B',
            'cta_text': 'Explore Texas Now!',
            'cta_url': 'https://www.traveltexas.com',
            'system_prompt': self.system_prompt
        }

    def count_tokens(self, text, model_name="gpt-3.5-turbo"):
        """Estimate token count using tiktoken"""
        try:
            encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
            return len(encoding.encode(text))
        except:
            # Fallback estimation: roughly 4 characters per token
            return len(text) // 4

    def call_openrouter_api_streaming(self, messages, api_key, model_config):
        """Call OpenRouter API with streaming - yields content chunks"""
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
        return {
            "role": "assistant",
            "content": "🤠 **DISCOVER TEXAS - YOUR ADVENTURE AWAITS!**\n\n🔥 **LIMITED TIME OFFERS:**\n• State Park Pass Bundle - ALL 89 parks for $70 (Save $200!)\n• BBQ Food Tours - Austin to Houston, 3 days $299\n• Cultural Heritage Trail - Historic sites + VIP access $199\n\n⭐ *\"Texas blew our minds! Best vacation ever!\"* - Travel Magazine\n\n**BOOK NOW before September 30th and get FREE dining vouchers!**\n\n*What Texas experience interests you most?*"
        }

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
