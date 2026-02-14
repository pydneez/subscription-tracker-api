from flask import Flask, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # Database Config
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///subscriptions.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # Register Blueprints
    from app.routes.subscription import bp as sub_bp 
    from app.routes.category import bp as cat_bp 
    from app.routes.analytics import bp as analytics_bp
    from app.routes.budgets import bp as budget_bp

    app.register_blueprint(sub_bp)
    app.register_blueprint(cat_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(budget_bp)

    with app.app_context():
        db.create_all()

    # Errors Handlers
    @app.errorhandler(400)
    def bad_request(error):
        return make_response(jsonify({'error': 'Bad Request', 'message': str(error.description)}), 400)

    @app.errorhandler(404)
    def not_found(error):
        message = error.description if error.description else "Resource not found"
        return make_response(jsonify({'error': 'Not Found', 'message': message}), 404)

    @app.errorhandler(500)
    def internal_error(error):
        return make_response(jsonify({'error': 'Internal Server Error', 'message': str(error)}), 500)

    @app.errorhandler(409)
    def conflict(error):
        message = error.description if error.description else "Duplicate Subscription Entry"
        return make_response(jsonify({'error': 'Duplicate Entry', 'message': message}), 409)
    return app

