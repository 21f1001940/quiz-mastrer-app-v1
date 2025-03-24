from app import app, db
from models import User

# Initialize database and create tables
with app.app_context():
    db.create_all()

    # Create predefined Admin user if not exists
    admin_email = "admin@example.com"
    existing_admin = User.query.filter_by(email=admin_email).first()
    
    if not existing_admin:
        admin = User(email=admin_email, username="Admin", is_admin=True)
        admin.set_password("admin123")  # Hashes the password
        db.session.add(admin)
        db.session.commit()

    print("Database setup complete!")
