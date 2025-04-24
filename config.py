import os

class Config:
    SECRET_KEY = 'your_secret_key_here'  # Replace with a strong key for CSRF protection
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'  # SQLite database
    SQLALCHEMY_TRACK_MODIFICATIONS = False
