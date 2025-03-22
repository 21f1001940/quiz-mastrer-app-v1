from flask import Flask
from models import db
from routers import user_bp  # Import Blueprint for user dashboard
from auth import auth_bp  # Import Blueprint for authentication

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz_app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "your_secret_key"

db.init_app(app)

# Register Blueprints
app.register_blueprint(user_bp)  # User routes
app.register_blueprint(auth_bp)  # Authentication routes

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create tables if they don't exist
    app.run(debug=True)
