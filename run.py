#!/usr/bin/env python3
"""
Main entry point for Phone Number Validator Flask application
Run this file to start the development server
"""

import os
from app import create_app

# Create Flask application
app = create_app()

if __name__ == '__main__':
    # Get port from environment variable or use default
    port = int(os.getenv('PORT', 5000))
    
    # Run the application
    app.run(
        host='0.0.0.0',
        port=port,
        debug=True
    )