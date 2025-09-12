"""
Analytics Dashboard for Travel Texas AI Agent
Provides cost analytics, usage trends, and reporting capabilities
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional
import json
from cost_engine import CostCalculationEngine
from budget_manager import BudgetManager


class AnalyticsDashboard:
    """Analytics dashboard with charts and reporting"""
    
    def __init__(self):
        self.cost_engine = CostCalculationEngine()
        self.budget_manager = BudgetManager()
    
    def generate_cost_comparison_table(self) -> pd.DataFrame:
        """Generate the cost comparison table like the example"""
        comparison_data = self.cost_engine.generate_cost_comparison_table()
        
        if not comparison_data:
            return pd.DataFrame()
        
        # Create DataFrame
        df = pd.DataFrame(comparison_data)
        
        # Rename columns to match the example format
        df = df.rename(columns={
            "model_name": "Model",
            "input_cost_per_million": "Cost per Mil Tokens - Input (USD)",
            "output_cost_per_million": "Cost per Mil Tokens - Output (USD)",
            "messages_per_session": "Number of Messages Per Session",
            "input_tokens_per_message": "Input Tokens per Message",
            "output_tokens_per_message": "Output Token Per Message",
            "total_cost_per_session": "Total Cost Per Session",
            "cost_per_million": "Cost_per_Mil"
        })
        
        # Select and reorder columns
        columns = [
            "Model",
            "Cost per Mil Tokens - Input (USD)",
            "Cost per Mil Tokens - Output (USD)",
            "Number of Messages Per Session",
            "Input Tokens per Message",
            "Output Token Per Message",
            "Cost_per_Mil",
            "Total Cost Per Session"
        ]
        
        return df[columns]
    
    def generate_usage_trends_chart(self, days: int = 30) -> go.Figure:
        """Generate usage trends chart"""
        historical_data = self.cost_engine.get_historical_data(days)
        sessions = historical_data.get("sessions", [])
        
        if not sessions:
            # Return empty chart
            fig = go.Figure()
            fig.add_annotation(
                text="No data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig
        
        # Prepare data for chart
        dates = []
        daily_costs = []
        daily_sessions = []
        
        # Group sessions by date
        sessions_by_date = {}
        for session in sessions:
            session_date = session.get("start_time", "")[:10]  # Extract date
            if session_date not in sessions_by_date:
                sessions_by_date[session_date] = {"cost": 0, "sessions": 0}
            
            sessions_by_date[session_date]["cost"] += session.get("total_cost", 0)
            sessions_by_date[session_date]["sessions"] += 1
        
        # Sort by date
        for date_str in sorted(sessions_by_date.keys()):
            dates.append(date_str)
            daily_costs.append(sessions_by_date[date_str]["cost"])
            daily_sessions.append(sessions_by_date[date_str]["sessions"])
        
        # Create chart
        fig = go.Figure()
        
        # Add cost line
        fig.add_trace(go.Scatter(
            x=dates,
            y=daily_costs,
            mode='lines+markers',
            name='Daily Cost ($)',
            yaxis='y',
            line=dict(color='#FF6B6B')
        ))
        
        # Add sessions bar
        fig.add_trace(go.Bar(
            x=dates,
            y=daily_sessions,
            name='Daily Sessions',
            yaxis='y2',
            marker_color='#4ECDC4',
            opacity=0.7
        ))
        
        # Update layout
        fig.update_layout(
            title="Usage Trends Over Time",
            xaxis_title="Date",
            yaxis=dict(
                title="Cost ($)",
                side="left",
                color='#FF6B6B'
            ),
            yaxis2=dict(
                title="Sessions",
                side="right",
                overlaying="y",
                color='#4ECDC4'
            ),
            hovermode='x unified',
            showlegend=True
        )
        
        return fig
    
    def generate_model_usage_pie_chart(self, days: int = 30) -> go.Figure:
        """Generate model usage pie chart"""
        historical_data = self.cost_engine.get_historical_data(days)
        sessions = historical_data.get("sessions", [])
        
        if not sessions:
            fig = go.Figure()
            fig.add_annotation(
                text="No data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig
        
        # Count model usage
        model_usage = {}
        for session in sessions:
            model = session.get("model_used", "Unknown")
            if model not in model_usage:
                model_usage[model] = {"sessions": 0, "cost": 0}
            
            model_usage[model]["sessions"] += 1
            model_usage[model]["cost"] += session.get("total_cost", 0)
        
        # Prepare data for pie chart
        labels = []
        values = []
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
        
        for i, (model, data) in enumerate(model_usage.items()):
            labels.append(f"{model}\n({data['sessions']} sessions)")
            values.append(data["cost"])
        
        # Create pie chart
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.3,
            marker_colors=colors[:len(labels)]
        )])
        
        fig.update_layout(
            title="Model Usage Distribution (by Cost)",
            showlegend=True
        )
        
        return fig
    
    def generate_budget_status_chart(self) -> go.Figure:
        """Generate budget status chart"""
        budgets = self.budget_manager.get_all_budgets()
        
        if not budgets:
            fig = go.Figure()
            fig.add_annotation(
                text="No budgets set",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig
        
        # Prepare data
        budget_types = []
        spent_amounts = []
        limit_amounts = []
        colors = []
        
        for budget in budgets:
            budget_type = budget["budget_type"]
            spent = budget["current_spent"]
            limit = budget["limit_amount"]
            
            budget_types.append(budget_type.title())
            spent_amounts.append(spent)
            limit_amounts.append(limit)
            
            # Color based on usage percentage
            percentage = (spent / limit) * 100 if limit > 0 else 0
            if percentage >= 100:
                colors.append('#FF6B6B')  # Red for exceeded
            elif percentage >= 80:
                colors.append('#FFEAA7')  # Yellow for warning
            else:
                colors.append('#96CEB4')  # Green for within limit
        
        # Create bar chart
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='Spent',
            x=budget_types,
            y=spent_amounts,
            marker_color=colors
        ))
        
        fig.add_trace(go.Bar(
            name='Limit',
            x=budget_types,
            y=limit_amounts,
            marker_color='lightgray',
            opacity=0.5
        ))
        
        fig.update_layout(
            title="Budget Status Overview",
            xaxis_title="Budget Type",
            yaxis_title="Amount ($)",
            barmode='group',
            showlegend=True
        )
        
        return fig
    
    def generate_cost_efficiency_report(self) -> Dict:
        """Generate cost efficiency report"""
        historical_data = self.cost_engine.get_historical_data(30)
        sessions = historical_data.get("sessions", [])
        
        if not sessions:
            return {"message": "No data available for analysis"}
        
        # Calculate metrics
        total_cost = sum(session.get("total_cost", 0) for session in sessions)
        total_sessions = len(sessions)
        total_messages = sum(session.get("total_messages", 0) for session in sessions)
        total_tokens = sum(session.get("total_input_tokens", 0) + session.get("total_output_tokens", 0) for session in sessions)
        
        # Calculate averages
        avg_cost_per_session = total_cost / total_sessions if total_sessions > 0 else 0
        avg_messages_per_session = total_messages / total_sessions if total_sessions > 0 else 0
        avg_cost_per_message = total_cost / total_messages if total_messages > 0 else 0
        avg_cost_per_token = total_cost / total_tokens if total_tokens > 0 else 0
        
        # Model efficiency analysis
        model_efficiency = {}
        for session in sessions:
            model = session.get("model_used", "Unknown")
            if model not in model_efficiency:
                model_efficiency[model] = {
                    "sessions": 0,
                    "total_cost": 0,
                    "total_tokens": 0,
                    "total_messages": 0
                }
            
            model_efficiency[model]["sessions"] += 1
            model_efficiency[model]["total_cost"] += session.get("total_cost", 0)
            model_efficiency[model]["total_tokens"] += session.get("total_input_tokens", 0) + session.get("total_output_tokens", 0)
            model_efficiency[model]["total_messages"] += session.get("total_messages", 0)
        
        # Calculate efficiency metrics for each model
        for model, data in model_efficiency.items():
            data["cost_per_session"] = data["total_cost"] / data["sessions"] if data["sessions"] > 0 else 0
            data["cost_per_message"] = data["total_cost"] / data["total_messages"] if data["total_messages"] > 0 else 0
            data["cost_per_token"] = data["total_cost"] / data["total_tokens"] if data["total_tokens"] > 0 else 0
        
        # Find most efficient model
        most_efficient_model = min(model_efficiency.items(), key=lambda x: x[1]["cost_per_token"])[0] if model_efficiency else "N/A"
        
        return {
            "period_days": 30,
            "total_cost": total_cost,
            "total_sessions": total_sessions,
            "total_messages": total_messages,
            "total_tokens": total_tokens,
            "avg_cost_per_session": avg_cost_per_session,
            "avg_messages_per_session": avg_messages_per_session,
            "avg_cost_per_message": avg_cost_per_message,
            "avg_cost_per_token": avg_cost_per_token,
            "model_efficiency": model_efficiency,
            "most_efficient_model": most_efficient_model,
            "recommendations": self._generate_recommendations(model_efficiency, avg_cost_per_token)
        }
    
    def _generate_recommendations(self, model_efficiency: Dict, avg_cost_per_token: float) -> List[str]:
        """Generate cost optimization recommendations"""
        recommendations = []
        
        if not model_efficiency:
            return ["No usage data available for recommendations"]
        
        # Find most and least efficient models
        sorted_models = sorted(model_efficiency.items(), key=lambda x: x[1]["cost_per_token"])
        
        if len(sorted_models) > 1:
            most_efficient = sorted_models[0]
            least_efficient = sorted_models[-1]
            
            efficiency_ratio = least_efficient[1]["cost_per_token"] / most_efficient[1]["cost_per_token"]
            
            if efficiency_ratio > 2:
                recommendations.append(
                    f"Consider using {most_efficient[0]} more often. "
                    f"It's {efficiency_ratio:.1f}x more cost-efficient than {least_efficient[0]}"
                )
        
        # Check for high usage of expensive models
        for model, data in model_efficiency.items():
            if data["cost_per_token"] > avg_cost_per_token * 1.5:
                recommendations.append(
                    f"{model} is significantly more expensive than average. "
                    f"Consider using it only for complex tasks."
                )
        
        # General recommendations
        if avg_cost_per_token > 0.0001:  # If cost per token is high
            recommendations.append("Consider using smaller models for simple tasks to reduce costs")
        
        if not recommendations:
            recommendations.append("Your current model usage appears cost-efficient!")
        
        return recommendations
    
    def export_analytics_data(self, format: str = "csv") -> str:
        """Export analytics data in specified format"""
        historical_data = self.cost_engine.get_historical_data(30)
        sessions = historical_data.get("sessions", [])
        
        if not sessions:
            return "No data available for export"
        
        # Create DataFrame
        df = pd.DataFrame(sessions)
        
        # Format timestamp
        if 'start_time' in df.columns:
            df['start_time'] = pd.to_datetime(df['start_time']).dt.strftime('%Y-%m-%d %H:%M:%S')
        
        if format.lower() == "csv":
            filename = f"analytics_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            df.to_csv(filename, index=False)
            return f"Data exported to {filename}"
        elif format.lower() == "json":
            filename = f"analytics_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            df.to_json(filename, orient='records', date_format='iso')
            return f"Data exported to {filename}"
        else:
            return "Unsupported format. Use 'csv' or 'json'"
