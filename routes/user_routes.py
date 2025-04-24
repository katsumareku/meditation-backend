from flask import Blueprint, request, jsonify
from models import db, User

user_bp = Blueprint('user', __name__)

@user_bp.route('/register', methods=['POST'])
def register_user():
    data = request.json
    device_id = data.get('device_id')
    
    if not device_id:
        return jsonify({"error": "Device ID is required"}), 400
    
    existing_user = User.query.filter_by(device_id=device_id).first()
    
    if existing_user:
        return jsonify({"message": "User already exists", "user_id": existing_user.id}), 200
    
    new_user = User(device_id=device_id)
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({"message": "User registered successfully", "user_id": new_user.id}), 201