"""
Budget Management System for Travel Texas AI Agent
Handles budget creation, tracking, and spending alerts
"""

import os
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional
from supabase_client import SupabaseClient


class BudgetManager:
    """Budget management system with Supabase integration"""
    
    def __init__(self):
        self.supabase = SupabaseClient()
    
    def create_daily_budget(self, limit_amount: float) -> bool:
        """Create a daily budget"""
        return self.supabase.create_budget("daily", limit_amount, date.today())
    
    def create_monthly_budget(self, limit_amount: float) -> bool:
        """Create a monthly budget"""
        return self.supabase.create_budget("monthly", limit_amount, date.today())
    
    def create_total_budget(self, limit_amount: float) -> bool:
        """Create a total budget"""
        return self.supabase.create_budget("total", limit_amount, date.today())
    
    def get_budget_status(self, budget_type: str = "daily") -> Dict:
        """Get budget status and spending information"""
        budget_data = self.supabase.get_budget_data(budget_type)
        
        if not budget_data:
            return {
                "status": "no_budget",
                "message": f"No {budget_type} budget set",
                "limit_amount": 0,
                "current_spent": 0,
                "remaining": 0,
                "percentage_used": 0
            }
        
        budget = budget_data[0]
        limit_amount = budget["limit_amount"]
        current_spent = budget["current_spent"]
        remaining = limit_amount - current_spent
        percentage_used = (current_spent / limit_amount) * 100 if limit_amount > 0 else 0
        
        # Determine status
        if percentage_used >= 100:
            status = "exceeded"
            message = f"⚠️ Budget exceeded! ({percentage_used:.1f}% used)"
        elif percentage_used >= 80:
            status = "warning"
            message = f"⚠️ Approaching budget limit ({percentage_used:.1f}% used)"
        else:
            status = "within_limit"
            message = f"✅ Within budget ({percentage_used:.1f}% used)"
        
        return {
            "status": status,
            "budget_type": budget_type,
            "limit_amount": limit_amount,
            "current_spent": current_spent,
            "remaining": remaining,
            "percentage_used": percentage_used,
            "message": message,
            "reset_date": budget.get("reset_date")
        }
    
    def get_all_budgets(self) -> List[Dict]:
        """Get all active budgets"""
        return self.supabase.get_budget_data()
    
    def reset_budget(self, budget_type: str) -> bool:
        """Reset budget spending to zero"""
        budget_data = self.supabase.get_budget_data(budget_type)
        
        if not budget_data:
            return False
        
        budget = budget_data[0]
        
        # Update budget to reset spending
        try:
            update_data = {
                "current_spent": 0.0,
                "reset_date": date.today().isoformat()
            }
            
            result = self.supabase.supabase.table("budgets").update(update_data).eq("id", budget["id"]).execute()
            return len(result.data) > 0
            
        except Exception as e:
            print(f"❌ Error resetting budget: {e}")
            return False
    
    def update_budget_limit(self, budget_type: str, new_limit: float) -> bool:
        """Update budget limit amount"""
        budget_data = self.supabase.get_budget_data(budget_type)
        
        if not budget_data:
            return False
        
        budget = budget_data[0]
        
        try:
            update_data = {
                "limit_amount": new_limit
            }
            
            result = self.supabase.supabase.table("budgets").update(update_data).eq("id", budget["id"]).execute()
            return len(result.data) > 0
            
        except Exception as e:
            print(f"❌ Error updating budget limit: {e}")
            return False
    
    def get_spending_summary(self, days: int = 30) -> Dict:
        """Get spending summary for the last N days"""
        sessions_data = self.supabase.get_analytics_data(days)
        
        total_cost = sum(session.get("total_cost", 0) for session in sessions_data)
        total_sessions = len(sessions_data)
        
        # Calculate daily average
        daily_average = total_cost / max(days, 1)
        
        # Get budget status
        daily_budget = self.get_budget_status("daily")
        monthly_budget = self.get_budget_status("monthly")
        
        return {
            "period_days": days,
            "total_spent": total_cost,
            "total_sessions": total_sessions,
            "daily_average": daily_average,
            "daily_budget_status": daily_budget,
            "monthly_budget_status": monthly_budget,
            "projected_monthly_spend": daily_average * 30
        }
    
    def check_spending_alerts(self) -> List[Dict]:
        """Check for spending alerts across all budgets"""
        alerts = []
        
        budgets = self.get_all_budgets()
        
        for budget in budgets:
            budget_type = budget["budget_type"]
            status = self.get_budget_status(budget_type)
            
            if status["status"] in ["exceeded", "warning"]:
                alerts.append({
                    "type": "budget_alert",
                    "budget_type": budget_type,
                    "status": status["status"],
                    "message": status["message"],
                    "percentage_used": status["percentage_used"],
                    "remaining": status["remaining"]
                })
        
        return alerts
    
    def get_cost_projection(self, budget_type: str = "daily", days_ahead: int = 7) -> Dict:
        """Project future spending based on current usage patterns"""
        # Get recent spending data
        recent_data = self.supabase.get_analytics_data(7)  # Last 7 days
        
        if not recent_data:
            return {
                "projection": 0,
                "confidence": "low",
                "message": "No recent data available for projection"
            }
        
        # Calculate average daily spending
        total_recent_cost = sum(session.get("total_cost", 0) for session in recent_data)
        avg_daily_spending = total_recent_cost / 7
        
        # Project future spending
        projected_spending = avg_daily_spending * days_ahead
        
        # Get current budget status
        budget_status = self.get_budget_status(budget_type)
        
        # Calculate if projection exceeds budget
        if budget_status["limit_amount"] > 0:
            projected_percentage = (projected_spending / budget_status["limit_amount"]) * 100
        else:
            projected_percentage = 0
        
        # Determine confidence level
        confidence = "high" if len(recent_data) >= 5 else "medium" if len(recent_data) >= 3 else "low"
        
        return {
            "projection": projected_spending,
            "days_ahead": days_ahead,
            "avg_daily_spending": avg_daily_spending,
            "confidence": confidence,
            "budget_limit": budget_status["limit_amount"],
            "projected_percentage": projected_percentage,
            "will_exceed_budget": projected_spending > budget_status["limit_amount"],
            "message": f"Projected spending: ${projected_spending:.2f} over {days_ahead} days"
        }
