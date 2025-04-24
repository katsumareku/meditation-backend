import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///meditation.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'your-secret-key'  # Change this to a random string