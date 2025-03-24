from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from models import db
from config import Config
from routes import app_routes  # Import routes

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)  # Load configurations

# Initialize database
db.init_app(app)

with app.app_context():
    db.create_all()

# Configure Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = "login"  # Redirect to login page if not authenticated

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

# Register routes from routes.py
app.register_blueprint(app_routes)

# Run the application
if __name__ == "__main__":
    app.run(debug=True)
