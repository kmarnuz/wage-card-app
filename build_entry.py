"""Single entry point for PyInstaller build."""
import sys
import os

# Set up paths
base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(base_dir, 'backend', 'src'))

# Import and run the app
from app import app
import uvicorn
import webbrowser
import threading
import time

def open_browser():
    time.sleep(2)
    webbrowser.open("http://localhost:8000")

if __name__ == "__main__":
    print("="*60)
    print("  GB WAGE CARD MANAGEMENT SYSTEM")
    print("  Opening in browser: http://localhost:8000")
    print("  Press Ctrl+C to stop")
    print("="*60)
    print()
    
    # Open browser automatically
    threading.Thread(target=open_browser, daemon=True).start()
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
