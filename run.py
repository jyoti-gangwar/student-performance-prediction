"""
Student Performance Prediction System - Application Runner
===========================================================
This runner automatically detects your environment and launches the application:
1. Launches the Flask server (Frontend UI + ML Prediction Backend API at http://127.0.0.1:5000).
2. Supports '--quick' mode for Python built-in HTTP server at http://127.0.0.1:8000.
"""

import sys
import os
import webbrowser
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"
BACKEND_DIR = BASE_DIR / "backend"

def run_server():
    print("=" * 70)
    print("  STUDENT PERFORMANCE PREDICTION SYSTEM - COLLEGE PBL PROJECT")
    print("=" * 70)

    # Check for explicit quick mode flag
    force_quick = "--quick" in sys.argv

    if not force_quick:
        try:
            import flask
            print("\n[+] Flask & ML environment detected. Launching Integrated Server...")
            sys.path.insert(0, str(BACKEND_DIR))
            from app import app
            
            url = "http://127.0.0.1:5000"
            print(f"[+] Full Application & ML Backend running at: {url}")
            print(f"[+] Open this URL in your web browser: {url}")
            print("[+] Press Ctrl+C to stop the server.\n")
            try:
                webbrowser.open(url)
            except Exception:
                pass
            app.run(host="127.0.0.1", port=5000, debug=False)
            return
        except ImportError:
            print("\n[!] Flask is not installed. Falling back to Quick HTTP Mode...")

    # Quick Mode (HTTP Server on Port 8000)
    import http.server
    import socketserver
    import functools

    PORT = 8000
    for arg in sys.argv:
        if arg.startswith("--port="):
            try:
                PORT = int(arg.split("=")[1])
            except ValueError:
                pass

    print(f"\n[i] Running in Quick Mode (Python built-in HTTP server).")
    Handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(FRONTEND_DIR))
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        url = f"http://127.0.0.1:{PORT}"
        print(f"\n[+] Frontend Application is RUNNING at: {url}")
        print(f"[+] Open this URL in your web browser: {url}")
        print("[+] Press Ctrl+C to stop the server.\n")
        try:
            webbrowser.open(url)
        except Exception:
            pass
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[-] Server stopped.")

if __name__ == "__main__":
    run_server()
