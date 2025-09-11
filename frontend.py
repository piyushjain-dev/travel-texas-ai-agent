"""
Frontend components for Travel Texas AI Agent
Handles Streamlit UI, user interactions, and display logic
"""

import streamlit as st
import time
from backend import TravelTexasBackend


class TravelTexasFrontend:
    """Frontend service for Travel Texas AI Agent"""
    
    def __init__(self):
        self.backend = TravelTexasBackend()
        self.init_session_state()

    def init_session_state(self):
        """Initialize Streamlit session state"""
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = [self.backend.get_welcome_message()]

        if 'token_usage' not in st.session_state:
            st.session_state.token_usage = {'input_tokens': 0, 'output_tokens': 0, 'total_tokens': 0}

        if 'openrouter_key' not in st.session_state:
            st.session_state.openrouter_key = ""

        if 'selected_model' not in st.session_state:
            st.session_state.selected_model = self.backend.default_model

    def render_sidebar(self):
        """Render the sidebar with controls"""
        with st.sidebar:
            st.image("https://www.traveltexas.com/sites/default/files/tto_logo_stacked.png", width=200)
            st.title("Travel Texas AI Agent")
            
            # Banner Image
            st.image("https://www.traveltexas.com/sites/default/files/texas-banner-hero.jpg", 
                    width=180, caption="Discover Texas!")
            
            # Call-to-Action Button (below banner)
            if st.button(
                "🚀 Explore Texas Now!",
                key="sidebar_cta_button",
                help="Visit Travel Texas website",
                width='stretch',
                type="primary"
            ):
                st.markdown("""
                <div style="text-align: center; padding: 15px; background-color: #f0f8ff; border-radius: 10px; margin: 10px 0;">
                    <h4>🌟 Ready to Explore Texas? 🌟</h4>
                    <p>Click below to discover amazing experiences!</p>
                    <a href="https://www.traveltexas.com" target="_blank" style="
                        display: inline-block;
                        background-color: #ff6b6b;
                        color: white;
                        padding: 10px 20px;
                        text-decoration: none;
                        border-radius: 20px;
                        font-weight: bold;
                    ">Visit TravelTexas.com</a>
                </div>
                """, unsafe_allow_html=True)

            # API Key input
            api_key = st.text_input(
                "OpenRouter API Key",
                value=st.session_state.openrouter_key,
                type="password",
                help="Get your API key from https://openrouter.ai"
            )

            if api_key != st.session_state.openrouter_key:
                st.session_state.openrouter_key = api_key

            st.markdown("---")

            # Model selection dropdown
            st.subheader("🤖 Model Selection")

            # Create options list with emoji and pricing
            model_options = {}
            available_models = self.backend.get_available_models()
            
            for key, info in available_models.items():
                if info.get('available', True):
                    label = f"{info['emoji']} {info['name']}"
                    model_options[label] = key

            # Handle case where selected model might not be available
            current_selection = st.session_state.selected_model
            if current_selection not in available_models:
                current_selection = self.backend.default_model
                st.session_state.selected_model = current_selection

            selected_label = st.selectbox(
                "Choose AI Model:",
                options=list(model_options.keys()),
                index=list(model_options.values()).index(current_selection),
                help="Select your preferred AI model"
            )

            # Update selected model
            new_selection = model_options[selected_label]
            if new_selection != st.session_state.selected_model:
                st.session_state.selected_model = new_selection
                st.rerun()

            # Display current model info with pricing
            current_model = available_models[st.session_state.selected_model]
            pricing = current_model.get('pricing', {})
            input_cost = pricing.get('input_tokens_per_million', 0)
            output_cost = pricing.get('output_tokens_per_million', 0)
            
            # Show cost estimation for typical conversation
            estimated_cost = self.backend.estimate_conversation_cost(st.session_state.selected_model)
            
            st.info(f"""
            **Current Model:** {current_model['emoji']} {current_model['name']}
            
            **Provider:** {current_model.get('provider', 'Unknown')}
            
            **Pricing:** ${input_cost:.2f} input / ${output_cost:.2f} output per 1M tokens
            
            **Est. Cost:** ~${estimated_cost['total_cost']:.4f} per conversation
            """)
            
            # Model comparison
            if st.checkbox("📊 Show Model Comparison", help="Compare all available models"):
                comparison_data = self.backend.get_model_comparison()
                
                st.subheader("💰 Cost Comparison")
                for model in comparison_data:
                    with st.expander(f"{model['emoji']} {model['name']} - ${model['estimated_conversation_cost']:.4f}/conversation"):
                        st.write(f"**Provider:** {model['provider']}")
                        st.write(f"**Description:** {model['description']}")
                        st.write(f"**Input Cost:** ${model['input_cost_per_million']:.2f}/1M tokens")
                        st.write(f"**Output Cost:** ${model['output_cost_per_million']:.2f}/1M tokens")
                        st.write(f"**Capabilities:** {', '.join(model['capabilities'])}")
                        st.write(f"**Estimated Cost:** ${model['estimated_conversation_cost']:.4f} per conversation")

            st.markdown("---")

            # Token usage summary with real costs
            st.subheader("📊 Usage & Costs")
            usage = st.session_state.token_usage
            
            # Calculate real costs for current model
            if usage['input_tokens'] > 0 or usage['output_tokens'] > 0:
                cost_data = self.backend.calculate_cost(
                    st.session_state.selected_model,
                    usage['input_tokens'],
                    usage['output_tokens']
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Input Tokens", f"{usage['input_tokens']:,}")
                    st.metric("Output Tokens", f"{usage['output_tokens']:,}")
                with col2:
                    st.metric("Total Tokens", f"{usage['total_tokens']:,}")
                    st.metric("Total Cost", f"${cost_data['total_cost']:.4f}")
                
                # Cost breakdown
                st.caption(f"💡 Input: ${cost_data['input_cost']:.4f} | Output: ${cost_data['output_cost']:.4f}")
            else:
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Input Tokens", "0")
                    st.metric("Output Tokens", "0")
                with col2:
                    st.metric("Total Tokens", "0")
                    st.metric("Total Cost", "$0.0000")

            st.markdown("---")

            # Cost Management Section
            st.subheader("💰 Cost Management")
            
            # Budget Status
            budget_status = self.backend.get_budget_status("daily")
            if budget_status["status"] != "no_budget":
                st.info(f"""
                **Daily Budget:** ${budget_status['limit_amount']:.2f}
                
                **Spent:** ${budget_status['current_spent']:.2f}
                
                **Remaining:** ${budget_status['remaining']:.2f}
                
                **Status:** {budget_status['message']}
                """)
            else:
                st.warning("No daily budget set")
                
                # Smart Budget Suggestions
                st.info("💡 **Smart Suggestions:**")
                analytics_data = self.backend.get_analytics_data(7)  # Last 7 days
                
                if analytics_data.get('total_cost', 0) > 0:
                    avg_daily = analytics_data['total_cost'] / 7
                    suggested_daily = avg_daily * 1.5  # 50% buffer
                    suggested_monthly = suggested_daily * 30
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"💡 Set ${suggested_daily:.2f}/day", key="suggested_daily"):
                            if self.backend.create_budget("daily", suggested_daily):
                                st.success(f"✅ Daily budget: ${suggested_daily:.2f}")
                                st.rerun()
                    
                    with col2:
                        if st.button(f"💡 Set ${suggested_monthly:.2f}/month", key="suggested_monthly"):
                            if self.backend.create_budget("monthly", suggested_monthly):
                                st.success(f"✅ Monthly budget: ${suggested_monthly:.2f}")
                                st.rerun()
                    
                    st.caption(f"Based on your last 7 days usage (avg: ${avg_daily:.2f}/day)")
                else:
                    st.caption("Start using the app to get personalized budget suggestions!")

                
                # Quick Setup Button
                st.markdown("---")
                if st.button("🚀 Quick Setup Budget", width='stretch', key="quick_setup"):
                    if self.backend.create_budget("daily", 5.00):
                        st.success("✅ Daily budget: $5.00")
                        st.rerun()
            
            # Budget Management
            with st.expander("🎯 Budget Settings"):
                budget_type = st.selectbox("Budget Type", ["daily", "monthly", "total"])
                
                # Quick Budget Presets
                st.subheader("💰 Quick Presets")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("$5/day", key="preset_5_daily"):
                        if self.backend.create_budget("daily", 5.00):
                            st.success("✅ Daily budget: $5.00")
                            st.rerun()
                
                with col2:
                    if st.button("$20/month", key="preset_20_monthly"):
                        if self.backend.create_budget("monthly", 20.00):
                            st.success("✅ Monthly budget: $20.00")
                            st.rerun()
                
                with col3:
                    if st.button("$50/month", key="preset_50_monthly"):
                        if self.backend.create_budget("monthly", 50.00):
                            st.success("✅ Monthly budget: $50.00")
                            st.rerun()
                
                st.markdown("---")
                
                # Custom Budget
                st.subheader("⚙️ Custom Budget")
                budget_amount = st.number_input("Budget Amount ($)", min_value=0.01, value=10.00, step=0.01)
                
                if st.button("Set Custom Budget"):
                    if self.backend.create_budget(budget_type, budget_amount):
                        st.success(f"✅ {budget_type.title()} budget: ${budget_amount:.2f}")
                        st.rerun()
                    else:
                        st.error("Failed to set budget")
            
            # Session Summary
            session_summary = self.backend.get_session_summary()
            if session_summary:
                st.subheader("📈 Current Session")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Messages", session_summary['total_messages'])
                    st.metric("Session Cost", f"${session_summary['total_cost']:.4f}")
                with col2:
                    st.metric("Input Tokens", f"{session_summary['total_input_tokens']:,}")
                    st.metric("Output Tokens", f"{session_summary['total_output_tokens']:,}")
            
            st.markdown("---")

            # Clear chat
            if st.button("🗑️ Clear Chat"):
                st.session_state.chat_history = [self.backend.get_welcome_message()]
                st.session_state.token_usage = {'input_tokens': 0, 'output_tokens': 0, 'total_tokens': 0}
                # End current session
                self.backend.end_cost_tracking_session()
                st.rerun()

    def render_header(self, model_config):
        """Render the main header section"""
        st.title(f"{model_config['emoji']} Welcome to Travel Texas!")
        st.markdown("**Chat with our AI agent to discover amazing Texas experiences and exclusive deals!**")

    def render_agent_info(self, model_config):
        """Render agent information card"""
        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:  # Center the chat interface
            # Agent header with model details
            pricing = model_config.get('pricing', {})
            input_cost = pricing.get('input_tokens_per_million', 0)
            output_cost = pricing.get('output_tokens_per_million', 0)
            
            st.markdown(f"""
            <div style="border-left: 4px solid {model_config['color']}; padding: 15px; margin-bottom: 20px; background-color: #f8f9fa;">
                <h3 style="margin: 0;">{model_config['emoji']} {model_config['name']}</h3>
                <p style="color: gray; font-size: 0.9em; margin: 5px 0;">Powered by {model_config['display_name']} ({model_config.get('provider', 'Unknown')})</p>
                <p style="color: #666; font-size: 0.8em; margin: 5px 0;">💰 ${input_cost:.2f} input / ${output_cost:.2f} output per 1M tokens</p>
                <p style="color: #666; font-size: 0.8em; margin: 5px 0;">🎯 {model_config.get('description', 'AI-powered Texas tourism assistant')}</p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("---")

    def render_chat_history(self):
        """Render the chat history"""
        chat_container = st.container()

        with chat_container:
            # Display chat history
            for message in st.session_state.chat_history:
                with st.chat_message(message["role"]):
                    st.write(message["content"])

    def handle_user_input(self, model_config):
        """Handle user input and generate AI response"""
        # Handle auto-prompt from helper buttons first
        if st.session_state.get('selected_prompt'):
            prompt = st.session_state.selected_prompt
            st.session_state.selected_prompt = None  # Clear it immediately
        else:
            # Regular chat input
            prompt = st.chat_input("Ask me about Texas adventures, food, culture, and more!")

        if prompt:
            if not self.backend.validate_api_key(st.session_state.openrouter_key):
                st.error("Please enter your OpenRouter API key in the sidebar!")
                return

            # Start cost tracking session if not already started
            if not hasattr(st.session_state, 'cost_session_started'):
                session_id = self.backend.start_cost_tracking_session(st.session_state.selected_model)
                st.session_state.cost_session_started = True
                st.session_state.cost_session_id = session_id

            # Log user message for cost tracking
            self.backend.log_user_message(prompt, st.session_state.selected_model)

            # Add user message to chat history
            st.session_state.chat_history.append({
                "role": "user",
                "content": prompt
            })

            # Display user message
            with st.chat_message("user"):
                st.write(prompt)

            # Prepare messages for API
            messages = [
                {"role": "system", "content": model_config['system_prompt']},
                *st.session_state.chat_history
            ]

            # Call API and get streaming response
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""
                
                try:
                    # Stream the response
                    for chunk in self.backend.call_openrouter_api_streaming(
                        messages, st.session_state.openrouter_key, model_config
                    ):
                        if chunk:
                            full_response += chunk
                            message_placeholder.write(full_response + "▌")
                            time.sleep(0.03)  # Small delay for better visual effect
                    
                    # Remove the cursor and show final response
                    message_placeholder.write(full_response)
                    
                    # Log assistant message for cost tracking
                    self.backend.log_assistant_message(full_response, st.session_state.selected_model)
                    
                    # Add assistant response to chat history
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": full_response
                    })

                    # Update token usage with real calculation
                    estimated_input_tokens = self.backend.count_tokens(prompt)
                    estimated_output_tokens = self.backend.count_tokens(full_response)
                    
                    st.session_state.token_usage['input_tokens'] += estimated_input_tokens
                    st.session_state.token_usage['output_tokens'] += estimated_output_tokens
                    st.session_state.token_usage['total_tokens'] += estimated_input_tokens + estimated_output_tokens

                    # Rerun to update metrics
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error generating response: {str(e)}")

    def render_analytics_dashboard(self):
        """Render the analytics dashboard"""
        st.title("📊 Cost Analytics Dashboard")
        
        # Tabs for different analytics views
        tab1, tab2, tab3, tab4 = st.tabs(["💰 Cost Comparison", "📈 Usage Trends", "🎯 Budget Status", "📋 Reports"])
        
        with tab1:
            st.subheader("Model Cost Comparison")
            comparison_data = self.backend.get_cost_comparison_table()
            
            if comparison_data:
                # Create DataFrame for display
                import pandas as pd
                df = pd.DataFrame(comparison_data)
                
                # Display table
                st.dataframe(df, width='stretch')
                
                # Display chart
                import plotly.express as px
                fig = px.bar(df, x='model_name', y='total_cost_per_session', 
                           title='Cost Per Session by Model',
                           color='total_cost_per_session',
                           color_continuous_scale='RdYlGn_r')
                st.plotly_chart(fig, width='stretch', key="cost_comparison_chart")
            else:
                st.info("No cost comparison data available")
        
        with tab2:
            st.subheader("Usage Trends")
            days = st.slider("Days to analyze", 1, 90, 30)
            
            # Usage trends chart
            trends_chart = self.backend.get_usage_trends_chart(days)
            st.plotly_chart(trends_chart, width='stretch', key="usage_trends_chart")
            
            # Model usage pie chart
            pie_chart = self.backend.get_model_usage_pie_chart(days)
            st.plotly_chart(pie_chart, width='stretch', key="model_usage_pie_chart")
        
        with tab3:
            st.subheader("Budget Status")
            
            # Budget status chart
            budget_chart = self.backend.get_budget_status_chart()
            st.plotly_chart(budget_chart, width='stretch', key="budget_status_chart")
            
            # Budget details
            col1, col2, col3 = st.columns(3)
            with col1:
                daily_budget = self.backend.get_budget_status("daily")
                st.metric("Daily Budget", f"${daily_budget.get('limit_amount', 0):.2f}", 
                         f"${daily_budget.get('current_spent', 0):.2f} spent")
            
            with col2:
                monthly_budget = self.backend.get_budget_status("monthly")
                st.metric("Monthly Budget", f"${monthly_budget.get('limit_amount', 0):.2f}", 
                         f"${monthly_budget.get('current_spent', 0):.2f} spent")
            
            with col3:
                total_budget = self.backend.get_budget_status("total")
                st.metric("Total Budget", f"${total_budget.get('limit_amount', 0):.2f}", 
                         f"${total_budget.get('current_spent', 0):.2f} spent")
        
        with tab4:
            st.subheader("Cost Efficiency Report")
            
            if st.button("Generate Report"):
                report = self.backend.get_cost_efficiency_report()
                
                if "message" in report:
                    st.info(report["message"])
                else:
                    # Display key metrics
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Cost (30d)", f"${report['total_cost']:.2f}")
                    with col2:
                        st.metric("Total Sessions", report['total_sessions'])
                    with col3:
                        st.metric("Avg Cost/Session", f"${report['avg_cost_per_session']:.4f}")
                    with col4:
                        st.metric("Most Efficient Model", report['most_efficient_model'])
                    
                    # Recommendations
                    st.subheader("💡 Recommendations")
                    for recommendation in report['recommendations']:
                        st.write(f"• {recommendation}")

    def render_main_app(self):
        """Render the main application"""
        # Create tabs for main app and analytics
        tab1, tab2 = st.tabs(["💬 Chat", "📊 Analytics"])
        
        with tab1:
            # Get current model configuration
            model_config = self.backend.get_model_config(st.session_state.selected_model)

            # Render header
            self.render_header(model_config)

            # Render agent info
            self.render_agent_info(model_config)

            # Render chat history
            self.render_chat_history()

            # Handle user input
            self.handle_user_input(model_config)
        
        with tab2:
            self.render_analytics_dashboard()

    def run(self):
        """Run the complete application"""
        # Page configuration
        st.set_page_config(
            page_title="Travel Texas AI Agent",
            page_icon="🤠",
            layout="wide",
            initial_sidebar_state="expanded"
        )

        # Render sidebar
        self.render_sidebar()

        # Render main app
        self.render_main_app()
