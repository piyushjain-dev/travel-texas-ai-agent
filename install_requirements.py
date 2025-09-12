"""
Script to install required dependencies for the Travel Texas AI Agent
"""

import subprocess
import sys

def install_requirements():
    """Install all required packages"""
    
    requirements = [
        "streamlit>=1.28.0",
        "requests>=2.31.0", 
        "python-dotenv>=1.0.0",
        "supabase>=2.0.0",
        "plotly>=5.17.0",
        "pandas>=2.0.0",
        "tiktoken>=0.5.0",
        "aiohttp>=3.8.0"  # Added missing aiohttp
    ]
    
    print("📦 Installing required packages...")
    
    for package in requirements:
        try:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ {package} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {package}: {e}")
    
    print("\n🎉 All packages installed!")
    print("🚀 You can now run the app with: streamlit run main.py")

if __name__ == "__main__":
    install_requirements()
