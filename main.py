"""
Travel Texas AI Agent - Main Entry Point
Clean, modular architecture with separated frontend and backend
"""

from frontend import TravelTexasFrontend


def main():
    """Main entry point for the Travel Texas AI Agent"""
    app = TravelTexasFrontend()
    app.run()


if __name__ == "__main__":
    main()