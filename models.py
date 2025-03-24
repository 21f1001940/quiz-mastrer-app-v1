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
    qualification = db.Column(db.String(100)) 
    dob = db.Column(db.Date) 
    password_hash = db.Column(db.String(200), nullable=False)  
    is_admin = db.Column(db.Boolean, default=False) 
    
    scores = db.relationship('Score', backref='user', lazy=True)


    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)    

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True, nullable=False)
    description = db.Column(db.Text)

    chapters = db.relationship('Chapter', backref='subject', lazy=True)

class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    name = db.Column(db.String(128), nullable=False)

    quizzes = db.relationship('Quiz', backref='chapter', lazy=True)

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable=False)
    date_of_quiz = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    time_duration = db.Column(db.String(10), nullable=False)
    total_qsn = db.Column(db.Integer, nullable=False, default=0)

    questions = db.relationship('Question', backref='quiz', lazy=True)
    scores = db.relationship('Score', backref='quiz', lazy=True)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    question_statement = db.Column(db.Text, nullable=False)
    option1 = db.Column(db.String(128))
    option2 = db.Column(db.String(128))
    option3 = db.Column(db.String(128))
    option4 = db.Column(db.String(128))
    correct_option = db.Column(db.String(10))
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable=False)

class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp_of_attempt = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    total_score = db.Column(db.Integer)
