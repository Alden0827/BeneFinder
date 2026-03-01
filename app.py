from flask import Flask, render_template
from flask_login import LoginManager
from models import db, User
from config import Config
from routes.auth import auth_bp
from routes.finder import finder_bp
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    app.register_blueprint(auth_bp)
    app.register_blueprint(finder_bp)

    @app.errorhandler(500)
    @app.errorhandler(Exception)
    def handle_exception(e):
        # Log the error if needed
        return render_template('error.html', error=str(e)), 500

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5001, debug=True)
