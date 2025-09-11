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
            st.session_state.selected_model = 'claude-3.5-sonnet'

    def render_sidebar(self):
        """Render the sidebar with controls"""
        with st.sidebar:
            st.image("https://www.traveltexas.com/sites/default/files/tto_logo_stacked.png", width=200)
            st.title("Travel Texas AI Agent")
            st.markdown("---")

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

            # Create options list with emoji
            model_options = {}
            for key, info in self.backend.get_available_models().items():
                label = f"{info['emoji']} {info['name']}"
                model_options[label] = key

            selected_label = st.selectbox(
                "Choose AI Model:",
                options=list(model_options.keys()),
                index=list(model_options.values()).index(st.session_state.selected_model),
                help="Different models have varying capabilities"
            )

            # Update selected model
            new_selection = model_options[selected_label]
            if new_selection != st.session_state.selected_model:
                st.session_state.selected_model = new_selection
                st.rerun()

            # Display current model info
            current_model = self.backend.get_available_models()[st.session_state.selected_model]
            st.info(f"""
            **Current Model:** {current_model['emoji']} {current_model['name']}
            """)

            st.markdown("---")

            # Token usage summary
            st.subheader("📊 Token Usage")
            usage = st.session_state.token_usage

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Input Tokens", f"{usage['input_tokens']:,}")
                st.metric("Output Tokens", f"{usage['output_tokens']:,}")
            with col2:
                st.metric("Total Tokens", f"{usage['total_tokens']:,}")

            st.markdown("---")

            # Clear chat
            if st.button("🗑️ Clear Chat"):
                st.session_state.chat_history = [self.backend.get_welcome_message()]
                st.session_state.token_usage = {'input_tokens': 0, 'output_tokens': 0, 'total_tokens': 0}
                st.rerun()

    def render_header(self, model_config):
        """Render the main header section"""
        st.title(f"{model_config['emoji']} Welcome to Travel Texas!")
        st.markdown("**Chat with our AI agent to discover amazing Texas experiences and exclusive deals!**")

    def render_agent_info(self, model_config):
        """Render agent information card"""
        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:  # Center the chat interface
            # Agent header
            st.markdown(f"""
            <div style="border-left: 4px solid {model_config['color']}; padding: 15px; margin-bottom: 20px; background-color: #f8f9fa;">
                <h3 style="margin: 0;">{model_config['emoji']} {model_config['name']}</h3>
                <p style="color: gray; font-size: 0.9em; margin: 5px 0;">Powered by {model_config['display_name']}</p>
            </div>
            """, unsafe_allow_html=True)

            # Call-to-action button
            if st.button(
                    f"🎯 {model_config['cta_text']}",
                    key="cta_button",
                    help="Visit Travel Texas website for exclusive experiences",
                    use_container_width=True
            ):
                st.markdown(f"[🌟 **{model_config['cta_text']}** - Opens in new tab]({model_config['cta_url']})")
                st.success("Click the link above to explore amazing Texas experiences on TravelTexas.com!")

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
                    
                    # Add assistant response to chat history
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": full_response
                    })

                    # Update token usage
                    estimated_usage = self.backend.estimate_token_usage(full_response)
                    st.session_state.token_usage['input_tokens'] += estimated_usage['input_tokens']
                    st.session_state.token_usage['output_tokens'] += estimated_usage['output_tokens']
                    st.session_state.token_usage['total_tokens'] += estimated_usage['total_tokens']

                    # Rerun to update metrics
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error generating response: {str(e)}")

    def render_main_app(self):
        """Render the main application"""
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
