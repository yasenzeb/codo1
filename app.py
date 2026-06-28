# -*- coding: utf-8 -*-
import sys
import os

# Expose local launcher for api/app.py
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "api"))
from app import app

if __name__ == "__main__":
    print("\n" + "="*50)
    print("🚀 LOCAL DEVELOPMENT SERVING FOR VERCELLABLE SYSTEM")
    print("🌐 URL: http://127.0.0.1:8000")
    print("="*50 + "\n")
    app.run(host="127.0.0.1", port=8000, debug=True)

