import os
from app import app
from waitress import serve

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    host = os.getenv("HOST", "0.0.0.0")
    print(f"Starting Production Waitress WSGI Server on http://{host}:{port}")
    serve(app, host=host, port=port, threads=8)
