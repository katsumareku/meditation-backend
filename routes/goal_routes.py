from flask import Blueprint, request, jsonify
from models import db, MeditationGoal, MeditationSession
from datetime import datetime, timezone, timedelta

goal_bp = Blueprint('goal', __name__)

@goal_bp.route('/goals', methods=['POST'])
def set_goal():
    data = request.json
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400
    
    existing_goal = MeditationGoal.query.filter_by(user_id=user_id).first()
    
    if existing_goal:
        existing_goal.daily_minutes = data.get('daily_minutes', existing_goal.daily_minutes)
        existing_goal.days_per_week = data.get('days_per_week', existing_goal.days_per_week)
        existing_goal.updated_at = datetime.utcnow()
    else:
        new_goal = MeditationGoal(
            user_id=user_id,
            daily_minutes=data.get('daily_minutes', 10),
            days_per_week=data.get('days_per_week', 7)
        )
        db.session.add(new_goal)
    
    db.session.commit()
    
    return jsonify({"message": "Goal set successfully"}), 200

@goal_bp.route('/goals', methods=['GET'])
def get_goal():
    user_id = request.args.get('user_id')
    
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400
    
    goal = MeditationGoal.query.filter_by(user_id=user_id).first()
    
    if not goal:
        return jsonify({"error": "No goal found for this user"}), 404
    
    # Use UTC timezone for consistency
    updated_at_str = goal.updated_at.replace(microsecond=0).astimezone(timezone.utc).isoformat()
    
    return jsonify({
        "daily_minutes": goal.daily_minutes,
        "days_per_week": goal.days_per_week,
        "updated_at": updated_at_str
    })

@goal_bp.route('/progress', methods=['GET'])
def get_progress():
    user_id = request.args.get('user_id')
    
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400
    
    today = datetime.utcnow().date()
    start_date = today - timedelta(days=6)
    
    # Fetch sessions from the last 7 days
    sessions = MeditationSession.query.filter(
        MeditationSession.user_id == user_id,
        MeditationSession.completed_at >= datetime.combine(start_date, datetime.min.time())
    ).all()
    
    # Fetch goal details
    goal = MeditationGoal.query.filter_by(user_id=user_id).first()
    daily_goal = goal.daily_minutes * 60 if goal else 600  # Default to 10 minutes in seconds
    
    # Initialize days_data structure
    days_data = { (start_date + timedelta(days=i)).isoformat(): {
        "date": (start_date + timedelta(days=i)).isoformat(),
        "total_seconds": 0,
        "goal_completed": False,
        "sessions": []
    } for i in range(7) }

    # Fill in session data for the last 7 days
    for session in sessions:
        session_date = session.completed_at.date().isoformat()
        if session_date in days_data:
            days_data[session_date]["total_seconds"] += session.duration
            days_data[session_date]["sessions"].append({
                "id": session.id,
                "duration": session.duration,
                "focus_rating": session.focus_rating
            })
    
    # Check if goals were met
    for date, data in days_data.items():
        data["goal_completed"] = data["total_seconds"] >= daily_goal
    
    # Calculate streak
    current_streak = longest_streak = temp_streak = 0
    
    # Loop to calculate the streak (start from today and go backward)
    for i in range(6, -1, -1):
        day = (today - timedelta(days=i)).isoformat()
        if days_data[day]["goal_completed"]:
            temp_streak += 1
            if i == 0:  # If today, set current streak
                current_streak = temp_streak
        else:
            longest_streak = max(longest_streak, temp_streak)
            temp_streak = 0
            if i == 0:  # If today, reset current streak if goal is not completed
                current_streak = 0
    
    longest_streak = max(longest_streak, temp_streak)
    
    return jsonify({
        "daily_goal_seconds": daily_goal,
        "days": list(days_data.values()),
        "current_streak": current_streak,
        "longest_streak": longest_streak
    })