from flask import Flask
from flask_cors import CORS
from models import db
from config import Config
from routes.meditation_routes import meditation_bp
from routes.user_routes import user_bp
from routes.goal_routes import goal_bp
from routes.health import health_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    CORS(app)
    
    # Register blueprints
    app.register_blueprint(meditation_bp, url_prefix='/api/meditation')
    app.register_blueprint(user_bp, url_prefix='/api/users')
    app.register_blueprint(goal_bp, url_prefix='/api/goals')
    app.register_blueprint(health_bp) 
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5001)