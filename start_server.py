#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple HTTP server to run the Run in Lyon web application.
Automatically opens the browser to the correct page.
"""
import http.server
import socketserver
import webbrowser
import os
import sys
from pathlib import Path

# Ensure UTF-8 output on Windows
if sys.platform == 'win32':
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')

PORT = 8000
DIRECTORY = Path(__file__).parent

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIRECTORY), **kwargs)

if __name__ == "__main__":
    print(f"Starting Run in Lyon server on port {PORT}...")
    print(f"Serving files from: {DIRECTORY}")

    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        url = f"http://localhost:{PORT}/web/"
        print(f"\nServer running at: {url}")
        print(f"Opening browser...")

        # Open browser
        webbrowser.open(url)

        print(f"\nPress Ctrl+C to stop the server\n")

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\nServer stopped. Goodbye!")
