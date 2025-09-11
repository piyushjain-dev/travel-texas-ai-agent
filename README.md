# Travel Texas AI Agent 🤠

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)

A modern, modular AI chat agent that promotes Texas tourism using various AI models through OpenRouter API. Built with clean architecture separating frontend and backend components.

## ✨ Features

- 🤖 **Multiple AI Models**: Claude, GPT-4, Llama support
- 💬 **Real-time Streaming**: ChatGPT-like text generation
- 📊 **Token Tracking**: Monitor API usage and costs
- 🎯 **Texas Tourism Focus**: Specialized prompts for travel recommendations
- 🔐 **Secure API Management**: Safe API key handling
- 🏗️ **Modular Architecture**: Clean separation of frontend and backend
- 📱 **Responsive Design**: Beautiful, modern UI with Streamlit

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- OpenRouter API key ([Get one here](https://openrouter.ai))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/travel-texas-ai-agent.git
   cd travel-texas-ai-agent
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   streamlit run main.py
   ```

4. **Open your browser**
   - Navigate to `http://localhost:8501`
   - Enter your OpenRouter API key in the sidebar
   - Start chatting about Texas!

## 🎯 Demo

![Travel Texas AI Agent Demo](https://via.placeholder.com/800x400/FF6B6B/FFFFFF?text=Travel+Texas+AI+Agent+Demo)

*Ask questions like:*
- "What are the best BBQ places in Austin?"
- "Plan a 3-day Texas road trip"
- "Tell me about Texas state parks"
- "What cultural experiences can I have in Houston?"

## 🏗️ Architecture

```
├── main.py          # Clean entry point
├── frontend.py      # Streamlit UI components
├── backend.py       # API logic and data processing
├── requirements.txt # Dependencies
└── README.md       # Documentation
```

### Backend (`backend.py`)
- API communication with OpenRouter
- Token counting and usage estimation
- Model configuration management
- Error handling and validation

### Frontend (`frontend.py`)
- Streamlit UI components
- User interaction handling
- Real-time streaming display
- Session state management

## 🤖 Available AI Models

| Model | Provider | Emoji | Best For |
|-------|----------|-------|----------|
| Claude 3.5 Sonnet | Anthropic | 🤠 | General conversations (Default) |
| Claude 3 Opus | Anthropic | 🧠 | Complex reasoning |
| Claude 3 Haiku | Anthropic | ⚡ | Fast responses |
| GPT-4o | OpenAI | 🚀 | Creative content |
| GPT-4o Mini | OpenAI | 💨 | Cost-effective |
| Llama 3.1 405B | Meta | 🦙 | Open-source alternative |

## ⚙️ Configuration

### Environment Variables (Optional)

Create a `.env` file:

```env
OPENROUTER_API_KEY=your_api_key_here
DEFAULT_MODEL=claude-3.5-sonnet
```

### Customization

- **System Prompts**: Modify the tourism-focused prompts in `backend.py`
- **UI Themes**: Customize colors and styling in `frontend.py`
- **Models**: Add or remove AI models in the `available_models` dictionary

## 📊 Usage Tracking

The application tracks:
- Input tokens (prompts sent to AI)
- Output tokens (responses received)
- Total token usage
- Estimated costs

## 🔧 Development

### Running in Development Mode

```bash
# Install development dependencies
pip install -r requirements.txt

# Run with auto-reload
streamlit run main.py --server.runOnSave true
```

### Project Structure

```
travel-texas-ai-agent/
├── main.py              # Application entry point
├── frontend.py          # UI components and interactions
├── backend.py           # API logic and data processing
├── requirements.txt     # Python dependencies
├── .gitignore          # Git ignore rules          
├── README.md           # This file
└── env_example.txt     # Environment variables template
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🐛 Troubleshooting

### Common Issues

- **API Key Error**: Ensure you have a valid OpenRouter API key
- **Model Not Available**: Some models may have usage limits
- **Connection Issues**: Check your internet connection
- **Import Errors**: Make sure all dependencies are installed

### Getting Help

- 📖 Check the [Streamlit Documentation](https://docs.streamlit.io)
- 🔗 Visit [OpenRouter API Docs](https://openrouter.ai/docs)
- 🐛 [Report Issues](https://github.com/yourusername/travel-texas-ai-agent/issues)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Streamlit](https://streamlit.io) for the amazing web framework
- [OpenRouter](https://openrouter.ai) for AI model access
- [Anthropic](https://anthropic.com), [OpenAI](https://openai.com), and [Meta](https://meta.ai) for the AI models
- Texas Tourism for inspiration! 🤠

## ⭐ Star This Repo

If you found this project helpful, please give it a star! ⭐

---

**Made with ❤️ for Texas tourism enthusiasts**
