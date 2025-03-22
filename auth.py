from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User

# Create Blueprint for authentication
auth_bp = Blueprint('auth', __name__)

# Route for user registration
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        qualification = request.form['qualification']
        dob = request.form['dob']

        # Check if the user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered. Please log in.', 'danger')
            return redirect(url_for('auth.register'))

        # Hash the password for security
        hashed_password = generate_password_hash(password)

        # Create new user
        new_user = User(username=username, email=email, password=hashed_password, qualification=qualification, dob=dob)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')

# Route for user login
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Find user in the database
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            flash('Login successful!', 'success')
            return redirect(url_for('user.dashboard'))  # Redirect to user dashboard
        else:
            flash('Invalid email or password. Please try again.', 'danger')

    return render_template('login.html')

# Route for user logout
@auth_bp.route('/logout')
def logout():
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
