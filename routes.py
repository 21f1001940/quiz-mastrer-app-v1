from flask import Blueprint, render_template, request, redirect, url_for, flash,session
from flask_login import login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_bcrypt import Bcrypt
from datetime import datetime, timezone
from models import *
from config import Config

# Create Blueprint for routes
app_routes = Blueprint("app_routes", __name__)

# Home Route - Redirect to login page
@app_routes.route("/")
def home():
    return redirect(url_for("app_routes.login"))

# User Registration Route
@app_routes.route("/app_routes.register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        username = request.form.get("username")
        qualification = request.form.get("qualification")
        # dob = request.form.get("dob")
        dob_str = request.form.get("dob")  # Get date as a string (e.g., "2000-05-15")
        dob = datetime.strptime(dob_str, "%Y-%m-%d").date()  
        password = request.form.get("password")

        # Check if email is already registered
        if User.query.filter_by(email=email).first():
            flash("Email already registered!", "danger")
            return redirect(url_for("app_routes.register"))

        # Create new user
        new_user = User(email=email, username=username, qualification=qualification, dob=dob)
        new_user.set_password(password)  # Hash the password
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! Please login.", "success")
        return redirect(url_for("app_routes.login"))

    return render_template("register.html")

# Login Route
@app_routes.route("/app_routes.login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()

        # Check credentials
        if user and user.check_password(password):
            login_user(user)
            flash("Login successful!", "success")

             # Redirect based on user role dynamically
            redirect_url = "app_routes.admin_dashboard" if user.is_admin else "app_routes.user_dashboard"

            return redirect(url_for(redirect_url))

        flash("Invalid email or password!", "danger")

    return render_template("login.html")

# Logout Route
@app_routes.route("/app_routes.logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully!", "info")
    return redirect(url_for("app_routes.login"))

# Admin Dashboard Route
@app_routes.route("/app_routes.admin_dashboard")
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        return redirect(url_for("app_routes.user_dashboard"))

    return render_template("admin_dashboard.html")

# User Dashboard Route
# @app_routes.route("/app_routes.user_dashboard")
# @login_required
# def user_dashboard():
#     return render_template("user_dashboard.html")

# from flask import render_template, session
# from your_app.models import User  # Import your User model
# from your_app import db

@app_routes.route('/app_routes.user_dashboard')
def user_dashboard():
    # Ensure user is logged in
    # user = User.query.filter_by(name=username).first()

    # user_id = session.get("user.id")  # Assuming you store user_id in session
    # if not user_id:
    #     return redirect(url_for('app_routes.login'))  # Redirect to login if not logged in

    # # Fetch user from database
    # user = User.query.get(id)

    # if not user:
    #     return "User not found", 404  # Handle case where user does not exist

    return render_template("user_dashboard.html", user=current_user)

