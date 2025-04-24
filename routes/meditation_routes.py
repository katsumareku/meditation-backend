from flask import Blueprint, request, jsonify
from models import db, MeditationSession
from datetime import datetime, timedelta

meditation_bp = Blueprint('meditation', __name__)

@meditation_bp.route('/sessions', methods=['POST'])
def add_session():
    data = request.json
    
    new_session = MeditationSession(
        user_id=data['user_id'],
        duration=data['duration'],
        focus_rating=data.get('focus_rating'),
        sound_used=data.get('sound_used')
    )
    
    db.session.add(new_session)
    db.session.commit()
    
    return jsonify({"message": "Session added successfully", "id": new_session.id}), 201

@meditation_bp.route('/sessions', methods=['GET'])
def get_sessions():
    user_id = request.args.get('user_id')
    days = request.args.get('days', default=30, type=int)
    
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400
    
    date_limit = datetime.utcnow() - timedelta(days=days)
    
    sessions = MeditationSession.query.filter(
        MeditationSession.user_id == user_id,
        MeditationSession.completed_at >= date_limit
    ).order_by(MeditationSession.completed_at.desc()).all()
    
    result = []
    for session in sessions:
        result.append({
            "id": session.id,
            "duration": session.duration,
            "completed_at": session.completed_at.isoformat(),
            "focus_rating": session.focus_rating,
            "sound_used": session.sound_used
        })
    
    return jsonify(result)