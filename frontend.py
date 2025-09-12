"""
Frontend components for Travel Texas AI Agent
Handles Streamlit UI, user interactions, and display logic
"""

import streamlit as st
import time
from backend import TravelTexasBackend
from agent_prompt_condensed import TEXAS_TOURISM_AGENT_PROMPT_CONDENSED as TEXAS_TOURISM_AGENT_PROMPT


class TravelTexasFrontend:
    """Frontend service for Travel Texas AI Agent"""
    
    def __init__(self):
        self._backend = None
        self.init_session_state()
    
    @property
    def backend(self):
        """Lazy initialization of backend"""
        if self._backend is None:
            self._backend = TravelTexasBackend()
        return self._backend

    def init_session_state(self):
        """Initialize Streamlit session state"""
        if 'chat_history' not in st.session_state:
            # Use a simple welcome message to avoid backend initialization
            welcome_msg = {
                "role": "assistant", 
                "content": "Howdy! Welcome to Travel Texas! I'm here to help you plan the perfect Texas adventure. What kind of experience are you looking for?"
            }
            st.session_state.chat_history = [welcome_msg]

        if 'token_usage' not in st.session_state:
            st.session_state.token_usage = {'input_tokens': 0, 'output_tokens': 0, 'total_tokens': 0}

        if 'selected_model' not in st.session_state:
            # Use default model without backend initialization
            st.session_state.selected_model = "google/gemini-2.5-flash"
        
        if 'is_processing' not in st.session_state:
            st.session_state.is_processing = False

    def render_sidebar(self):
        """Render the sidebar with controls"""
        with st.sidebar:
            st.image("Texas.webp", width=450)
            st.title("Travel Texas AI Agent")
            

            st.markdown("---")

            # Model selection dropdown
            st.subheader(" Model Selection")

            # Create options list with emoji and pricing
            model_options = {}
            available_models = self.backend.get_available_models()
            
            for key, info in available_models.items():
                if info.get('available', True):
                    label = f"{info['name']}"
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

            new_selection = model_options[selected_label]
            if new_selection != st.session_state.selected_model:
                st.session_state.selected_model = new_selection

            # Display current model info with pricing
            current_model = available_models[st.session_state.selected_model]
            pricing = current_model.get('pricing', {})
            input_cost = pricing.get('input_tokens_per_million', 0)
            output_cost = pricing.get('output_tokens_per_million', 0)
            
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

            # Session Summary - Use cached data to avoid startup delay
            if hasattr(st.session_state, 'token_usage') and st.session_state.token_usage['total_tokens'] > 0:
                st.subheader("📈 Current Session")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Messages", len(st.session_state.chat_history) - 1)  # Exclude welcome message
                    st.metric("Session Cost", f"${st.session_state.token_usage.get('total_cost', 0):.4f}")
                with col2:
                    st.metric("Input Tokens", f"{st.session_state.token_usage['input_tokens']:,}")
                    st.metric("Output Tokens", f"{st.session_state.token_usage['output_tokens']:,}")
            
            if st.button("🗑️ Clear Chat"):
                st.session_state.chat_history = [self.backend.get_welcome_message()]
                st.session_state.token_usage = {'input_tokens': 0, 'output_tokens': 0, 'total_tokens': 0}
                # End current session
                self.backend.end_cost_tracking_session()
                st.success("Chat cleared!")
            
            st.markdown("---")

    def render_header(self, model_config):
        """Render the main header section"""
        st.title(f"{model_config['emoji']} Welcome to Travel Texas!")
        st.markdown("**Chat with our AI agent to discover amazing Texas experiences and exclusive deals!**")

    def render_agent_info(self, model_config):
        """Render banner image and call-to-action button"""
        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:  # Center the banner and button
            # Use Streamlit native functions for reliable rendering
            st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
            
            # Banner Image - Replace with your local JPG image
            try:
                # Try to load local banner image first
                st.image("dallas_banner.jpg", width=700)
            except:
                # Fallback to online image if local file doesn't exist
                st.image("https://www.traveltexas.com/sites/default/files/texas-banner-hero.jpg", 
                        width=700)
            
            # Creative text with Discover Texas link - Mobile Compatible
            st.markdown("""
            <div style="
                text-align: center; 
                margin: 15px 0; 
                padding: 12px; 
                background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); 
                border-radius: 8px; 
                border-left: 3px solid #0066cc;
                max-width: 100%;
                box-sizing: border-box;
            ">
                <p style="
                    margin: 0 0 8px 0; 
                    font-size: clamp(14px, 4vw, 16px); 
                    color: #495057; 
                    font-style: italic;
                    line-height: 1.4;
                ">
                    🌟 "Everything's bigger in Texas" - and so are the adventures waiting for you! 🌟
                </p>
                <p style="
                    margin: 0; 
                    font-size: clamp(12px, 3.5vw, 14px); 
                    color: #6c757d;
                    line-height: 1.3;
                ">
                    From the bustling streets of Dallas to the serene landscapes of Big Bend, 
                    your perfect Texas experience awaits...
                </p>
                <a href="https://www.traveltexas.com" target="_blank" style="
                    display: inline-block;
                    margin-top: 8px;
                    font-weight: bold;
                    font-size: clamp(16px, 4.5vw, 18px);
                    color: #0066cc;
                    text-decoration: underline;
                    transition: color 0.3s ease;
                    padding: 4px 8px;
                    border-radius: 4px;
                ">Discover Texas!</a>
            </div>
            """, unsafe_allow_html=True)
            
            
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("---")

    def render_chat_history(self):
        """Render the chat history with smooth scrolling"""
        chat_container = st.container()
        
        with chat_container:
            # Display chat history with better styling
            for i, message in enumerate(st.session_state.chat_history):
                with st.chat_message(message["role"]):
                    if (message["role"] == "assistant" and 
                        i == len(st.session_state.chat_history) - 1 and 
                        message["content"] == "" and
                        st.session_state.is_processing):
                        self.stream_response_in_place(message, i)
                    else:
                        st.write(message["content"])

    def handle_user_input(self, model_config):
        """Handle user input and generate AI response"""
        if st.session_state.is_processing:
            return

        prompt = st.chat_input(
            "Ask me about Texas adventures, food, culture, and more!",
            disabled=st.session_state.is_processing
        )

        if prompt and not st.session_state.is_processing:
            st.session_state.is_processing = True

            # Add user message to chat history
            st.session_state.chat_history.append({
                "role": "user",
                "content": prompt
            })
            
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": ""
            })
            
            st.rerun()

    def stream_response_in_place(self, message, message_index):
        """Stream response directly in the chat message placeholder"""
        # Start cost tracking session if not already started
        if not hasattr(st.session_state, 'cost_session_started'):
            session_id = self.backend.start_cost_tracking_session(st.session_state.selected_model)
            st.session_state.cost_session_started = True
            st.session_state.cost_session_id = session_id

        # Get the user's last message
        user_message = st.session_state.chat_history[-2]["content"]
        
        # Log user message for cost tracking
        self.backend.log_user_message(user_message, st.session_state.selected_model)

        # Prepare messages for API
        messages = [
            {"role": "system", "content": TEXAS_TOURISM_AGENT_PROMPT},
            *st.session_state.chat_history[:-1]  # Exclude the empty assistant message
        ]
        
        def response_generator():
            full_response = ""
            try:
                model_config = self.backend.get_model_config(st.session_state.selected_model)
                for chunk in self.backend.call_openrouter_api_streaming(messages, model_config):
                    if chunk:
                        full_response += chunk
                        yield chunk
                
                st.session_state.chat_history[message_index]["content"] = full_response
                
                # Log assistant message for cost tracking
                self.backend.log_assistant_message(full_response, st.session_state.selected_model)

                # Update token usage
                user_input_tokens = self.backend.count_tokens(user_message)
                estimated_output_tokens = self.backend.count_tokens(full_response)
                
                if not hasattr(st.session_state, 'system_prompt_counted'):
                    st.session_state.system_prompt_counted = True
                    system_prompt_tokens = self.backend.count_tokens(TEXAS_TOURISM_AGENT_PROMPT)
                    total_input_tokens = user_input_tokens + system_prompt_tokens
                else:
                    total_input_tokens = user_input_tokens
                
                st.session_state.token_usage['input_tokens'] += total_input_tokens
                st.session_state.token_usage['output_tokens'] += estimated_output_tokens
                st.session_state.token_usage['total_tokens'] += total_input_tokens + estimated_output_tokens
                
            except Exception as e:
                error_msg = f"Error: {str(e)}"
                st.session_state.chat_history[message_index]["content"] = error_msg
                yield error_msg
            
            finally:
                st.session_state.is_processing = False
        
        st.write_stream(response_generator())

    def check_pending_response(self):
        """Check if there's a pending response to stream - no longer needed"""
        pass

    def stream_response(self, prompt, model_config):
        """Stream the assistant response - no longer needed"""
        pass

    def render_analytics_dashboard(self):
        """Render the analytics dashboard"""
        st.title("📊 Cost Analytics Dashboard")
        
        # Model Cost Comparison section with refresh button
        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader("Model Cost Comparison")
        with col2:
            if st.button(
                "🔄 Refresh Data", 
                key="refresh_analytics", 
                type="primary",
                width='stretch'
            ):
                st.rerun()
        
        # Fetch live data from Supabase
        comparison_data = self.backend.get_cost_comparison_table()
        
        if comparison_data:
            # Use analytics dashboard for formatted display
            from analytics_dashboard import AnalyticsDashboard
            analytics = AnalyticsDashboard()
            df = analytics.generate_cost_comparison_table()
            
            # Display table
            st.dataframe(df, width='stretch')
            
            # Display chart
            import plotly.express as px
            fig = px.bar(df, x='Model', y='Cost_per_Mil', 
                       title='Cost Per Mil by Model (Live Data)',
                       color='Cost_per_Mil',
                       color_continuous_scale='RdYlGn_r')
            
            # Make axis labels bold
            fig.update_layout(
                xaxis_title_font=dict(size=14, family="Arial", color="black"),
                yaxis_title_font=dict(size=14, family="Arial", color="black")
            )
            
            st.plotly_chart(fig, width='stretch', key="cost_comparison_chart")
        else:
            st.info("No cost comparison data available. Start chatting to generate data!")
            st.markdown("""
            **💡 Tips:**
            - Start a conversation with different models to generate usage data
            - Data is automatically saved to Supabase for persistence
            - Use the refresh button to update the dashboard with latest data
            """)

    def _generate_sample_data(self):
        """Generate sample usage data for testing"""
        try:
            # Generate sample sessions and messages for different models
            models = ["openai/gpt-4.1-mini", "google/gemini-2.5-flash"]
            
            for model_id in models:
                # Create a sample session
                session_id = self.backend.start_cost_tracking_session(model_id)
                
                # Add sample messages
                self.backend.log_user_message(session_id, "Tell me about Texas attractions")
                self.backend.log_assistant_message(session_id, "Texas has amazing attractions like the Alamo, Big Bend National Park, and Austin's music scene!")
                
                # End the session
                self.backend.end_cost_tracking_session(session_id)
                
        except Exception as e:
            st.error(f"Error generating sample data: {str(e)}")

    def render_main_app(self):
        """Render the main application"""
        try:
            with open('styles.css', 'r') as f:
                css_content = f.read()
        except FileNotFoundError:
            css_content = """
            /* ChatGPT-like styling */
            .stChatMessage {
                margin-bottom: 1rem;
                animation: fadeIn 0.3s ease-in;
            }
            
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            /* Keep input at bottom */
            .stChatInput {
                position: sticky;
                bottom: 0;
                background: white;
                z-index: 100;
                margin-top: 2rem;
            }
            
            /* Smooth scrolling */
            .main .block-container {
                padding-bottom: 6rem;
            }
            """
        
        st.markdown(f"""
        <style>
        {css_content}
        </style>
        """, unsafe_allow_html=True)
        
        # Create tabs for main app and analytics
        tab1, tab2 = st.tabs(["💬 Chat", "📊 Analytics"])
        
        with tab1:
            # Get current model configuration
            model_config = self.backend.get_model_config(st.session_state.selected_model)

            # Render header
            self.render_header(model_config)

            # Render agent info
            self.render_agent_info(model_config)

            self.render_chat_history()

            # Handle user input - this stays at the bottom
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
