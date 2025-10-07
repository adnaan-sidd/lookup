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
    app.config['WTF_CSRF_ENABLED'] = True
    app.config['WTF_CSRF_TIME_LIMIT'] = 3600  # 1 hour
    
    # Initialize CSRF protection
    CSRFProtect(app)
    
    # Register blueprints
    from app.routes import main
    app.register_blueprint(main)
    
    return app