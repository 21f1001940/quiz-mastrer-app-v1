from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from models import *
from config import Config
from routes import app_routes  
from datetime import datetime
# app = Flask(__name__)
# app.config.from_object(Config)  
# db.init_app(app)

# with app.app_context():
#     db.create_all()

# login_manager = LoginManager(app)
# login_manager.login_view = "login"  # Redirect to login page if not authenticated

# @login_manager.user_loader
# def load_user(user_id):
#     from models import User
#     return db.session.get(User, int(user_id)) 

# app.register_blueprint(app_routes)

# if __name__ == "__main__":
#     app.run(debug=True)

  

app = Flask(__name__)
app.config.from_object(Config)  
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = "login"  # Redirect to login page if not authenticated

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id)) 

# Register Blueprint for routes
app.register_blueprint(app_routes)

# Database setup (ensure Admin exists)
with app.app_context():
    db.create_all()

    # Create predefined Admin user if not exists
    admin_email = "admin@example.com"
    existing_admin = User.query.filter_by(role='admin').first()
    
    if not existing_admin:
        dob_str = "1980-01-01"  # Example input
        dob = datetime.strptime(dob_str, "%Y-%m-%d").date()
        admin = User(
            username="Admin",
            email=admin_email,
            role="admin",
            qualification="Master in Computer Science",
            dob=dob

            
            
        )
        admin.set_password("admin123")  # Hash password
        db.session.add(admin)
        db.session.commit()
        print("Admin user created.")
    # with app.app_context():
    # db.create_all()
        print("Database setup complete!")

if __name__ == "__main__":
    app.run(debug=True)
