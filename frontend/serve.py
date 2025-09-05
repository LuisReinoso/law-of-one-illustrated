#!/usr/bin/env python3
"""
Super Simple HTTP Server for Storybook Frontend
Just serves files and opens browser - that's it!
"""

import http.server
import socketserver
import webbrowser
import threading
import time

PORT = 8000

def open_browser():
    time.sleep(1)
    webbrowser.open(f'http://localhost:{PORT}')

if __name__ == "__main__":
    # Start browser in background
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Serve files
    Handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"🌟 Storybook viewer running at http://localhost:{PORT}")
        print("📖 Use Ctrl+C to stop")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")