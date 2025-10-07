"""
Phone Number Validator Web App
Flask application for validating phone numbers using multiple APIs
"""

from flask import Flask
from flask_wtf.csrf import CSRFProtect
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    
    # Temporarily disable CSRF for debugging
    app.config['WTF_CSRF_ENABLED'] = False
    
    # Initialize CSRF protection (disabled for now)
    # CSRFProtect(app)
    
    # Register blueprints
    from app.routes import main
    app.register_blueprint(main)
    
    return app