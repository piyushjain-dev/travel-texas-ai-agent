"""
Cost Calculation Engine for Travel Texas AI Agent
Handles real-time cost calculations, session tracking, and budget management
"""

import os
import json
import uuid
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple
from supabase_client import SupabaseClient


class CostCalculationEngine:
    """Advanced cost calculation engine with database integration"""
    
    def __init__(self):
        self.supabase = SupabaseClient()
        self.current_session_id = None
        self.session_data = {
            "total_cost": 0.0,
            "total_messages": 0,
            "total_input_tokens": 0,
            "total_output_tokens": 0,
            "messages": []
        }
        
        # Note: Database tables should be created manually using supabase_schema.sql
        # self.supabase.create_tables()
    
    def start_session(self, model_used: str) -> str:
        """Start a new session"""
        self.current_session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
        # Reset session data
        self.session_data = {
            "total_cost": 0.0,
            "total_messages": 0,
            "total_input_tokens": 0,
            "total_output_tokens": 0,
            "messages": []
        }
        
        # Create session in database
        self.supabase.create_session(self.current_session_id, model_used)
        
        return self.current_session_id
    
    def calculate_message_cost(self, model_id: str, input_tokens: int, output_tokens: int) -> Dict:
        """Calculate cost for a single message"""
        # Load model pricing from config
        try:
            with open("models_config.json", "r") as f:
                config = json.load(f)
                models = config.get("models", {})
                
            if model_id not in models:
                return {"input_cost": 0, "output_cost": 0, "total_cost": 0}
                
            model_info = models[model_id]
            pricing = model_info.get("pricing", {})
            
            input_cost_per_million = pricing.get("input_tokens_per_million", 0)
            output_cost_per_million = pricing.get("output_tokens_per_million", 0)
            
            # Calculate costs
            input_cost = (input_tokens / 1_000_000) * input_cost_per_million
            output_cost = (output_tokens / 1_000_000) * output_cost_per_million
            total_cost = input_cost + output_cost
            
            return {
                "input_cost": input_cost,
                "output_cost": output_cost,
                "total_cost": total_cost,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens
            }
            
        except Exception as e:
            print(f"❌ Error calculating message cost: {e}")
            return {"input_cost": 0, "output_cost": 0, "total_cost": 0}
    
    def log_message(self, message_type: str, input_tokens: int, output_tokens: int, 
                   model_used: str, content: str = "") -> Dict:
        """Log a message and update session totals"""
        if not self.current_session_id:
            self.start_session(model_used)
        
        # Calculate message cost
        cost_data = self.calculate_message_cost(model_used, input_tokens, output_tokens)
        
        # Update session data
        self.session_data["total_cost"] += cost_data["total_cost"]
        self.session_data["total_messages"] += 1
        self.session_data["total_input_tokens"] += input_tokens
        self.session_data["total_output_tokens"] += output_tokens
        
        # Add message to session
        message_data = {
            "type": message_type,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost": cost_data["total_cost"],
            "model_used": model_used,
            "timestamp": datetime.now().isoformat(),
            "content": content[:100] if content else ""
        }
        self.session_data["messages"].append(message_data)
        
        # Log to database
        self.supabase.log_message(
            self.current_session_id, message_type, input_tokens, 
            output_tokens, cost_data["total_cost"], model_used, content
        )
        
        # Update session in database
        self.supabase.update_session(
            self.current_session_id,
            self.session_data["total_cost"],
            self.session_data["total_messages"],
            self.session_data["total_input_tokens"],
            self.session_data["total_output_tokens"]
        )
        
        return cost_data
    
    def get_session_summary(self) -> Dict:
        """Get current session summary"""
        if not self.current_session_id:
            return {}
            
        return {
            "session_id": self.current_session_id,
            "total_cost": self.session_data["total_cost"],
            "total_messages": self.session_data["total_messages"],
            "total_input_tokens": self.session_data["total_input_tokens"],
            "total_output_tokens": self.session_data["total_output_tokens"],
            "avg_cost_per_message": self.session_data["total_cost"] / max(self.session_data["total_messages"], 1),
            "messages": self.session_data["messages"]
        }
    
    def calculate_cost_per_million_tokens(self, model_id: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost per million tokens"""
        cost_data = self.calculate_message_cost(model_id, input_tokens, output_tokens)
        total_tokens = input_tokens + output_tokens
        
        if total_tokens == 0:
            return 0.0
            
        return (cost_data["total_cost"] / total_tokens) * 1_000_000
    
    def generate_cost_comparison_table(self) -> List[Dict]:
        """Generate cost comparison table like the example"""
        try:
            with open("models_config.json", "r") as f:
                config = json.load(f)
                models = config.get("models", {})
            
            comparison_data = []
            
            # Standard session parameters
            messages_per_session = 5
            input_tokens_per_message = 350
            output_tokens_per_message = 500
            
            for model_id, model_info in models.items():
                if not model_info.get("available", True):
                    continue
                    
                pricing = model_info.get("pricing", {})
                input_cost_per_million = pricing.get("input_tokens_per_million", 0)
                output_cost_per_million = pricing.get("output_tokens_per_million", 0)
                
                # Calculate costs
                total_input_tokens = messages_per_session * input_tokens_per_message
                total_output_tokens = messages_per_session * output_tokens_per_message
                
                input_cost = (total_input_tokens / 1_000_000) * input_cost_per_million
                output_cost = (total_output_tokens / 1_000_000) * output_cost_per_million
                total_cost_per_session = input_cost + output_cost
                
                total_tokens = total_input_tokens + total_output_tokens
                cost_per_million = (total_cost_per_session / total_tokens) * 1_000_000
                
                comparison_data.append({
                    "model_id": model_id,
                    "model_name": model_info["name"],
                    "provider": model_info.get("provider", "Unknown"),
                    "emoji": model_info["emoji"],
                    "input_cost_per_million": input_cost_per_million,
                    "output_cost_per_million": output_cost_per_million,
                    "messages_per_session": messages_per_session,
                    "input_tokens_per_message": input_tokens_per_message,
                    "output_tokens_per_message": output_tokens_per_message,
                    "total_cost_per_session": round(total_cost_per_session, 6),
                    "cost_per_million": round(cost_per_million, 2)
                })
            
            # Sort by cost per million (cheapest first)
            comparison_data.sort(key=lambda x: x["cost_per_million"])
            
            return comparison_data
            
        except Exception as e:
            print(f"❌ Error generating cost comparison: {e}")
            return []
    
    def get_historical_data(self, days: int = 30) -> Dict:
        """Get historical usage data"""
        sessions_data = self.supabase.get_analytics_data(days)
        
        total_sessions = len(sessions_data)
        total_cost = sum(session.get("total_cost", 0) for session in sessions_data)
        total_messages = sum(session.get("total_messages", 0) for session in sessions_data)
        total_input_tokens = sum(session.get("total_input_tokens", 0) for session in sessions_data)
        total_output_tokens = sum(session.get("total_output_tokens", 0) for session in sessions_data)
        
        return {
            "period_days": days,
            "total_sessions": total_sessions,
            "total_cost": total_cost,
            "total_messages": total_messages,
            "total_input_tokens": total_input_tokens,
            "total_output_tokens": total_output_tokens,
            "avg_cost_per_session": total_cost / max(total_sessions, 1),
            "avg_messages_per_session": total_messages / max(total_sessions, 1),
            "sessions": sessions_data
        }
    
    def check_budget_limits(self, budget_type: str = "daily") -> Dict:
        """Check if spending is within budget limits"""
        budget_data = self.supabase.get_budget_data(budget_type)
        
        if not budget_data:
            return {"status": "no_budget", "message": f"No {budget_type} budget set"}
        
        budget = budget_data[0]
        limit_amount = budget["limit_amount"]
        current_spent = budget["current_spent"]
        
        percentage_used = (current_spent / limit_amount) * 100 if limit_amount > 0 else 0
        
        status = "within_limit"
        if percentage_used >= 100:
            status = "exceeded"
        elif percentage_used >= 80:
            status = "warning"
        
        return {
            "status": status,
            "budget_type": budget_type,
            "limit_amount": limit_amount,
            "current_spent": current_spent,
            "remaining": limit_amount - current_spent,
            "percentage_used": percentage_used,
            "message": self._get_budget_message(status, percentage_used)
        }
    
    def _get_budget_message(self, status: str, percentage: float) -> str:
        """Get budget status message"""
        if status == "exceeded":
            return f"⚠️ Budget exceeded! ({percentage:.1f}% used)"
        elif status == "warning":
            return f"⚠️ Approaching budget limit ({percentage:.1f}% used)"
        else:
            return f"✅ Within budget ({percentage:.1f}% used)"
    
    def end_session(self):
        """End current session"""
        if self.current_session_id:
            # Final update to database
            self.supabase.update_session(
                self.current_session_id,
                self.session_data["total_cost"],
                self.session_data["total_messages"],
                self.session_data["total_input_tokens"],
                self.session_data["total_output_tokens"]
            )
            
            # Update budget spending
            self.supabase.update_budget_spending("daily", self.session_data["total_cost"])
            
            self.current_session_id = None
            self.session_data = {
                "total_cost": 0.0,
                "total_messages": 0,
                "total_input_tokens": 0,
                "total_output_tokens": 0,
                "messages": []
            }
