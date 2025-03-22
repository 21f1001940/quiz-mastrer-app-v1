from flask import Blueprint, render_template, session, redirect, url_for, flash
from models import db, User, Quiz, Score

user_bp = Blueprint('user', __name__)

@user_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash("Please log in first!", "warning")
        return redirect(url_for('auth.login'))

    user = User.query.get(session['user_id'])
    quizzes = Quiz.query.all()
    scores = Score.query.filter_by(user_id=user.id).all()

    return render_template('dashboard.html', user=user, quizzes=quizzes, scores=scores)

@user_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("You have been logged out!", "info")
    return redirect(url_for('auth.login'))
