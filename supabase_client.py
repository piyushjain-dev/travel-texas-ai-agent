"""
Supabase client for Travel Texas AI Agent
Handles database operations for cost tracking, sessions, and analytics
"""

import os
import streamlit as st
from supabase import create_client, Client
from typing import Dict, List, Optional
import json
from datetime import datetime, date, timedelta
import uuid


class SupabaseClient:
    """Supabase client for database operations"""
    
    def __init__(self):
        # Get Supabase credentials from Streamlit secrets (for deployment) or environment variables (for local)
        try:
            # Try Streamlit secrets first (for deployment)
            self.url = st.secrets["SUPABASE_URL"]
            self.key = st.secrets["SUPABASE_KEY"]
        except:
            # Fallback to environment variables (for local development)
            self.url = os.getenv("SUPABASE_URL", "https://tvwygzsooodvzeyhkezu.supabase.co")
            self.key = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR2d3lnenNvb29kdnpleWhrZXp1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTc1Nzk2NTUsImV4cCI6MjA3MzE1NTY1NX0.hrU-itiLF53QqudWKFuz7jCpCKIEtoCD0ymkNMqIQ2Y")
        
        try:
            self.supabase: Client = create_client(self.url, self.key)
            # Only print success message once
            if not hasattr(SupabaseClient, '_initialized'):
                print("✅ Supabase client initialized successfully")
                SupabaseClient._initialized = True
        except Exception as e:
            print(f"❌ Error initializing Supabase client: {e}")
            self.supabase = None
    
    def create_tables(self):
        """Create database tables if they don't exist"""
        if not self.supabase:
            return False
            
        try:
            # Create sessions table
            sessions_sql = """
            CREATE TABLE IF NOT EXISTS sessions (
                id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
                session_id TEXT UNIQUE,
                start_time TIMESTAMP WITH TIME ZONE,
                end_time TIMESTAMP WITH TIME ZONE,
                total_cost DECIMAL(10,6),
                model_used TEXT,
                total_messages INTEGER,
                total_input_tokens INTEGER,
                total_output_tokens INTEGER,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            """
            
            # Create messages table
            messages_sql = """
            CREATE TABLE IF NOT EXISTS messages (
                id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
                session_id TEXT REFERENCES sessions(session_id),
                message_type TEXT CHECK (message_type IN ('user', 'assistant')),
                input_tokens INTEGER,
                output_tokens INTEGER,
                cost DECIMAL(10,6),
                timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                model_used TEXT,
                content TEXT
            );
            """
            
            # Create budgets table
            budgets_sql = """
            CREATE TABLE IF NOT EXISTS budgets (
                id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
                budget_type TEXT CHECK (budget_type IN ('daily', 'monthly', 'total')),
                limit_amount DECIMAL(10,2),
                current_spent DECIMAL(10,2) DEFAULT 0,
                reset_date DATE,
                is_active BOOLEAN DEFAULT true,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            """
            
            # Create usage_analytics table
            analytics_sql = """
            CREATE TABLE IF NOT EXISTS usage_analytics (
                id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
                date DATE,
                model_used TEXT,
                total_sessions INTEGER,
                total_messages INTEGER,
                total_cost DECIMAL(10,6),
                avg_cost_per_session DECIMAL(10,6),
                avg_tokens_per_message INTEGER,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            """
            
            # Execute SQL commands
            self.supabase.rpc('exec_sql', {'sql': sessions_sql}).execute()
            self.supabase.rpc('exec_sql', {'sql': messages_sql}).execute()
            self.supabase.rpc('exec_sql', {'sql': budgets_sql}).execute()
            self.supabase.rpc('exec_sql', {'sql': analytics_sql}).execute()
            
            print("✅ Database tables created successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error creating tables: {e}")
            return False
    
    def create_session(self, session_id: str, model_used: str) -> bool:
        """Create a new session"""
        if not self.supabase:
            return False
            
        try:
            session_data = {
                "session_id": session_id,
                "start_time": datetime.now().isoformat(),
                "model_used": model_used,
                "total_cost": 0.0,
                "total_messages": 0,
                "total_input_tokens": 0,
                "total_output_tokens": 0
            }
            
            result = self.supabase.table("sessions").insert(session_data).execute()
            return len(result.data) > 0
            
        except Exception as e:
            print(f"❌ Error creating session: {e}")
            return False
    
    def log_message(self, session_id: str, message_type: str, input_tokens: int, 
                   output_tokens: int, cost: float, model_used: str, content: str = "") -> bool:
        """Log a message to the database"""
        if not self.supabase:
            return False
            
        try:
            message_data = {
                "session_id": session_id,
                "message_type": message_type,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cost": cost,
                "model_used": model_used,
                "content": content[:1000] if content else ""  # Limit content length
            }
            
            result = self.supabase.table("messages").insert(message_data).execute()
            return len(result.data) > 0
            
        except Exception as e:
            print(f"❌ Error logging message: {e}")
            return False
    
    def update_session(self, session_id: str, total_cost: float, total_messages: int,
                      total_input_tokens: int, total_output_tokens: int) -> bool:
        """Update session totals"""
        if not self.supabase:
            return False
            
        try:
            update_data = {
                "total_cost": total_cost,
                "total_messages": total_messages,
                "total_input_tokens": total_input_tokens,
                "total_output_tokens": total_output_tokens,
                "end_time": datetime.now().isoformat()
            }
            
            result = self.supabase.table("sessions").update(update_data).eq("session_id", session_id).execute()
            return len(result.data) > 0
            
        except Exception as e:
            print(f"❌ Error updating session: {e}")
            return False
    
    def get_session_data(self, session_id: str) -> Optional[Dict]:
        """Get session data"""
        if not self.supabase:
            return None
            
        try:
            result = self.supabase.table("sessions").select("*").eq("session_id", session_id).execute()
            return result.data[0] if result.data else None
            
        except Exception as e:
            print(f"❌ Error getting session data: {e}")
            return None
    
    def get_messages_for_session(self, session_id: str) -> List[Dict]:
        """Get all messages for a session"""
        if not self.supabase:
            return []
            
        try:
            result = self.supabase.table("messages").select("*").eq("session_id", session_id).order("timestamp").execute()
            return result.data
            
        except Exception as e:
            print(f"❌ Error getting messages: {e}")
            return []
    
    def create_budget(self, budget_type: str, limit_amount: float, reset_date: date = None) -> bool:
        """Create a new budget"""
        if not self.supabase:
            return False
            
        try:
            budget_data = {
                "budget_type": budget_type,
                "limit_amount": limit_amount,
                "current_spent": 0.0,
                "reset_date": reset_date.isoformat() if reset_date else date.today().isoformat(),
                "is_active": True
            }
            
            result = self.supabase.table("budgets").insert(budget_data).execute()
            return len(result.data) > 0
            
        except Exception as e:
            print(f"❌ Error creating budget: {e}")
            return False
    
    def update_budget_spending(self, budget_type: str, additional_cost: float) -> bool:
        """Update budget spending"""
        if not self.supabase:
            return False
            
        try:
            # Get current budget
            result = self.supabase.table("budgets").select("*").eq("budget_type", budget_type).eq("is_active", True).execute()
            
            if not result.data:
                return False
                
            current_budget = result.data[0]
            new_spent = current_budget["current_spent"] + additional_cost
            
            update_data = {
                "current_spent": new_spent
            }
            
            result = self.supabase.table("budgets").update(update_data).eq("id", current_budget["id"]).execute()
            return len(result.data) > 0
            
        except Exception as e:
            print(f"❌ Error updating budget: {e}")
            return False
    
    def get_budget_data(self, budget_type: str = None) -> List[Dict]:
        """Get budget data"""
        if not self.supabase:
            return []
            
        try:
            query = self.supabase.table("budgets").select("*").eq("is_active", True)
            
            if budget_type:
                query = query.eq("budget_type", budget_type)
                
            result = query.execute()
            return result.data
            
        except Exception as e:
            print(f"❌ Error getting budget data: {e}")
            return []
    
    def get_analytics_data(self, days: int = 30) -> List[Dict]:
        """Get analytics data for the last N days"""
        if not self.supabase:
            return []
            
        try:
            # Get sessions data
            result = self.supabase.table("sessions").select("*").gte("created_at", 
                (datetime.now() - timedelta(days=days)).isoformat()).execute()
            
            return result.data
            
        except Exception as e:
            print(f"❌ Error getting analytics data: {e}")
            return []
    
    def test_connection(self) -> bool:
        """Test Supabase connection"""
        if not self.supabase:
            return False
            
        try:
            # Try to query a simple table
            result = self.supabase.table("sessions").select("id").limit(1).execute()
            return True
            
        except Exception as e:
            print(f"❌ Supabase connection test failed: {e}")
            return False
