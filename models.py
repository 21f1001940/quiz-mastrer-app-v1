from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_bcrypt import Bcrypt
from datetime import datetime, timezone

# Initialize database and bcrypt for password hashing
db = SQLAlchemy()
bcrypt = Bcrypt()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)  
    email = db.Column(db.String(100), unique=True, nullable=False)  
    username = db.Column(db.String(100), nullable=False)
    qualification = db.Column(db.String(100), nullable=False) 
    dob = db.Column(db.Date, nullable=False) 
    password_hash = db.Column(db.String(200), nullable=False)  
    isadmin = db.Column(db.Boolean, default=False) 
    role = db.Column(db.String(10), nullable=False, default="user")  # "admin" or "user"

    scores = db.relationship('Score', backref='user', lazy=True, passive_deletes=True)

    @property
    def is_admin(self):
        """Returns True if the user is an admin, otherwise False"""
        return self.role == "admin" or self.isadmin

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)    


    def get_id(self):
        return str(self.id)  # Ensure Flask-Login compatibility

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True, nullable=False)
    description = db.Column(db.Text)

    chapters = db.relationship('Chapter', backref='subject', cascade="all, delete-orphan", passive_deletes=True, lazy=True)

class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id', ondelete="CASCADE"), nullable=False)
    name = db.Column(db.String(128), nullable=False)

    quizzes = db.relationship('Quiz', backref='chapter', cascade="all, delete-orphan", passive_deletes=True, lazy=True)

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id', ondelete="CASCADE"), nullable=False)
    date_of_quiz = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    time_duration = db.Column(db.Integer, nullable=False)
    total_qsn = db.Column(db.Integer, nullable=False, default=0)

    questions = db.relationship('Question', backref='quiz', cascade="all, delete-orphan", passive_deletes=True, lazy=True)
    scores = db.relationship('Score', backref='quiz', cascade="all, delete-orphan", passive_deletes=True, lazy=True)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id', ondelete="CASCADE"), nullable=False)
    question_title = db.Column(db.String, nullable=False)
    question_statement = db.Column(db.Text, nullable=False)
    option1 = db.Column(db.String(128))
    option2 = db.Column(db.String(128))
    option3 = db.Column(db.String(128))
    option4 = db.Column(db.String(128))
    correct_option = db.Column(db.String(10), nullable=False)

class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id', ondelete="CASCADE"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    timestamp_of_attempt = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    total_score = db.Column(db.Integer)



    