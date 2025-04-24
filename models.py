from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(64), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))  # Use timezone-aware datetime
    sessions = db.relationship('MeditationSession', backref='user', lazy=True)
    goals = db.relationship('MeditationGoal', backref='user', lazy=True)

class MeditationSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # In seconds
    completed_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))  # Use timezone-aware datetime
    focus_rating = db.Column(db.Integer, nullable=True)  # Scale 1-5
    sound_used = db.Column(db.String(50), nullable=True)

class MeditationGoal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    daily_minutes = db.Column(db.Integer, default=10)
    days_per_week = db.Column(db.Integer, default=7)
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))  # Use timezone-aware datetime