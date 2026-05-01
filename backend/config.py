"""
Configuration settings for the Flask application
"""
import os

class Config:
    """Base configuration"""
    # Database configuration
    SQLALCHEMY_DATABASE_URI = 'sqlite:///todos.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # CORS configuration
    CORS_ORIGINS = ['http://localhost:8080']
    
    # JSON configuration
    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = True

# Made with Bob
