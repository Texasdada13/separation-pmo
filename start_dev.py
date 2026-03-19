#!/usr/bin/env python
"""Development Server Startup Script for Separation PMO"""
import os
import sys
import socket
import webbrowser
import threading
import time

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)


def find_free_port(start=5200, end=5299):
    """Find a free port in the given range."""
    for port in range(start, end):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('127.0.0.1', port))
            sock.close()
            return port
        except OSError:
            continue
    raise RuntimeError(f"No free ports found in range {start}-{end}")


def open_browser(port, delay=2.0):
    """Open browser after a delay to allow server to start."""
    time.sleep(delay)
    url = f"http://localhost:{port}"
    print(f"\n  Opening browser: {url}")
    webbrowser.open(url)


def load_demo_data():
    """Create app and load demo data if database is empty."""
    from web.app import create_app
    from src.database.models import Program

    app = create_app()
    with app.app_context():
        if Program.query.count() == 0:
            print("  Loading demo separation data...")
            # seed() creates its own app, so call it standalone
            from scripts.seed_demo import seed
            seed()
            print("  Demo data loaded")
        else:
            print("  Demo data already exists")

    return app


def main():
    """Start the development server."""
    print("=" * 60)
    print("  Separation PMO - Development Server")
    print("=" * 60)

    # Use assigned port (5200)
    port = 5200
    print(f"\n  Using port: {port}")

    # Load demo data and create app
    app = load_demo_data()

    # Start browser opener in background
    browser_thread = threading.Thread(target=open_browser, args=(port,))
    browser_thread.daemon = True
    browser_thread.start()

    # Start the server
    print(f"\n  Starting server at http://localhost:{port}")
    print("   Press Ctrl+C to stop\n")

    app.run(host='127.0.0.1', port=port, debug=True, use_reloader=False)


if __name__ == '__main__':
    main()
