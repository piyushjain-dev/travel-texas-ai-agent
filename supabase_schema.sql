-- Supabase Database Schema for Travel Texas AI Agent
-- Run this SQL in your Supabase SQL Editor

-- Create sessions table
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

-- Create messages table
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

-- Create budgets table
CREATE TABLE IF NOT EXISTS budgets (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    budget_type TEXT CHECK (budget_type IN ('daily', 'monthly', 'total')),
    limit_amount DECIMAL(10,2),
    current_spent DECIMAL(10,2) DEFAULT 0,
    reset_date DATE,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create usage_analytics table
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

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_sessions_session_id ON sessions(session_id);
CREATE INDEX IF NOT EXISTS idx_messages_session_id ON messages(session_id);
CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp);
CREATE INDEX IF NOT EXISTS idx_budgets_type_active ON budgets(budget_type, is_active);
CREATE INDEX IF NOT EXISTS idx_analytics_date ON usage_analytics(date);

-- Enable Row Level Security (RLS)
ALTER TABLE sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE budgets ENABLE ROW LEVEL SECURITY;
ALTER TABLE usage_analytics ENABLE ROW LEVEL SECURITY;

-- Create policies for public access (adjust as needed for your security requirements)
CREATE POLICY "Allow all operations on sessions" ON sessions FOR ALL USING (true);
CREATE POLICY "Allow all operations on messages" ON messages FOR ALL USING (true);
CREATE POLICY "Allow all operations on budgets" ON budgets FOR ALL USING (true);
CREATE POLICY "Allow all operations on usage_analytics" ON usage_analytics FOR ALL USING (true);
