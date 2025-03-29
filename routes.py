from flask import Blueprint, render_template, request, redirect, url_for, flash,session
from flask_login import login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_bcrypt import Bcrypt
from datetime import datetime, timezone
from models import *
from config import Config
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend for Matplotlib
import matplotlib.pyplot as plt
import io
import base64


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
        dob_str = request.form.get("dob") # Get date as a string (e.g., "2000-05-15")
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



@app_routes.route('/admin_dashboard', methods=['GET'])
@login_required
def admin_dashboard():
    try:
        subjects = Subject.query.outerjoin(Chapter).outerjoin(Quiz).all()
        return render_template('admin_dashboard.html', subjects=subjects)

    except Exception as e:
        flash(f"Error loading admin dashboard: {str(e)}", "error")
        print(f"Error loading admin dashboard: {str(e)}")
        return redirect(url_for('app_routes.admin_dashboard'))  



# Add Subject
@app_routes.route('/add_subject', methods=['POST'])
@login_required
def add_subject():
    try:
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()

        if not name or not description:
            flash('Both name and description are required', 'error')
            return redirect(url_for('app_routes.admin_dashboard'))

        existing_subject = Subject.query.filter_by(name=name).first()
        if existing_subject:
            flash('Subject already exists.', 'error')
            return redirect(url_for('app_routes.admin_dashboard'))

        new_sub = Subject(name=name, description=description)
        db.session.add(new_sub)
        db.session.commit()

        flash('Subject added successfully.', 'success')
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'Database error: {str(e)}', 'error')
    except Exception as e:
        flash(f'Unexpected error: {str(e)}', 'error')

    return redirect(url_for('app_routes.admin_dashboard'))


# Update Subject
@app_routes.route('/update_subject/<int:id>', methods=['POST'])
@login_required
def update_subject(id):
    try:
        subject = Subject.query.get(id)
        if not subject:
            flash('Subject not found', 'error')
            return redirect(url_for('app_routes.admin_dashboard'))

        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()

        if not name or not description:
            flash('Both name and description are required', 'error')
            return redirect(url_for('app_routes.admin_dashboard'))

        existing_subject = Subject.query.filter(Subject.name == name, Subject.id != id).first()
        if existing_subject:
            flash('A subject with this name already exists.', 'error')
            return redirect(url_for('app_routes.admin_dashboard'))

        subject.name = name
        subject.description = description
        db.session.commit()

        flash('Subject updated successfully.', 'success')
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'Database error: {str(e)}', 'error')
    except Exception as e:
        flash(f'Unexpected error: {str(e)}', 'error')

    return redirect(url_for('app_routes.admin_dashboard'))




@app_routes.route('/delete_subject/<int:id>', methods=['POST'])
@login_required
def delete_subject(id):
    try:
        subject = Subject.query.get_or_404(id)
        db.session.delete(subject)
        db.session.commit()

        flash("Subject deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting subject: {str(e)}", "error")

    return redirect(url_for('app_routes.admin_dashboard'))


@app_routes.route('/add_chapter/<int:subject_id>', methods=['POST'])
@login_required
def add_chapter(subject_id):
    try:
        name = request.form.get('name', '').strip()
        print(f"Received chapter name: {name}, Subject ID: {subject_id}")  # Debugging

        if not name:
            flash('Chapter name is required', 'error')
            return redirect(url_for('app_routes.admin_dashboard'))

        existing_chapter = Chapter.query.filter_by(name=name, subject_id=subject_id).first()
        if existing_chapter:
            flash('A chapter with this name already exists.', 'error')
            return redirect(url_for('app_routes.admin_dashboard'))

        new_chapter = Chapter(name=name, subject_id=subject_id)
        db.session.add(new_chapter)
        db.session.commit()

        flash('Chapter added successfully.', 'success')
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'Database error: {str(e)}', 'error')
    except Exception as e:
        flash(f'Unexpected error: {str(e)}', 'error')

    return redirect(url_for('app_routes.admin_dashboard'))



# Update Chapter
@app_routes.route('/update_chapter/<int:id>', methods=['POST'])
@login_required
def update_chapter(id):
    try:
        chapter = Chapter.query.get(id)
        if not chapter:
            flash('Chapter not found', 'error')
            return redirect(url_for('app_routes.admin_dashboard'))

        name = request.form.get('name', '').strip()
        if not name:
            flash('Chapter name is required', 'error')
            return redirect(url_for('app_routes.admin_dashboard'))

        existing_chapter = Chapter.query.filter(Chapter.name == name, Chapter.id != id).first()
        if existing_chapter:
            flash('A chapter with this name already exists.', 'error')
            return redirect(url_for('app_routes.admin_dashboard'))

        chapter.name = name
        db.session.commit()

        flash('Chapter updated successfully.', 'success')
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'Database error: {str(e)}', 'error')
    except Exception as e:
        flash(f'Unexpected error: {str(e)}', 'error')

    return redirect(url_for('app_routes.admin_dashboard'))


# Delete Chapter
@app_routes.route('/delete_chapter/<int:id>', methods=['POST'])
@login_required
def delete_chapter(id):
    try:
        chapter = Chapter.query.get(id)
        if not chapter:
            flash('Chapter not found', 'error')
            return redirect(url_for('app_routes.admin_dashboard'))
        
        # Delete chapter
        db.session.delete(chapter)
        db.session.commit()

        flash('Chapter deleted successfully.', 'success')
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'Database error: {str(e)}', 'error')
    except Exception as e:
        flash(f'Unexpected error: {str(e)}', 'error')

    return redirect(url_for('app_routes.admin_dashboard'))




# quiz and question operations routes .............



# - List all quizzes
@app_routes.route("/quiz_mngmnt")
def quiz_mngmnt():
    chapters = Chapter.query.all()
    questions = Question.query.all() 
    quizzes = Quiz.query.order_by(Quiz.id.desc()).all() 
    return render_template("quiz_mngmnt.html", quizzes=quizzes,chapters=chapters,questions=questions)


# add quiz route
@app_routes.route("/add_quiz", methods=["POST"])
def add_quiz():
    quiz_name = request.form.get("quiz_name")
    quiz_duration = request.form.get("quiz_duration")
    selected_chapter_id = request.form.get("chapter_id")  # Selected from dropdown
    # new_chapter_name = request.form.get("new_chapter_name") last change

    # Validate quiz details
    if not quiz_name or not quiz_duration:
        flash("Quiz name and duration are required!", "danger")
        return redirect(url_for("app_routes.quiz_mngmnt"))

    # Determine the chapter to use
    if selected_chapter_id:  # If user selects an existing chapter
        try:
            chapter_id = int(selected_chapter_id)
        except ValueError:
            flash("Invalid Chapter ID!", "danger")
            return redirect(url_for("app_routes.quiz_mngmnt"))

        # Ensure the chapter exists
        chapter = Chapter.query.get(chapter_id)
        if not chapter:
            flash("Selected chapter does not exist!", "danger")
            return redirect(url_for("app_routes.quiz_mngmnt"))

    # elif new_chapter_name:  # If user enters a new chapter name
    #     # Check if chapter already exists
    #     existing_chapter = Chapter.query.filter_by(name=new_chapter_name).first()
    #     if existing_chapter:
    #         chapter_id = existing_chapter.id  # Use existing chapter ID
    #     else:
    #         # Create a new chapter
    #         new_chapter = Chapter(name=new_chapter_name)
    #         db.session.add(new_chapter)
    #         db.session.commit()
    #         chapter_id = new_chapter.id  # Get newly created chapter ID
    else:
        flash("Please select a chapter or enter a new chapter name!", "danger")
        return redirect(url_for("app_routes.quiz_mngmnt"))

    # Create the quiz
    new_quiz = Quiz(
        name=quiz_name,
        chapter_id=chapter_id,  # Now included
        time_duration=int(quiz_duration),
        total_qsn=0  # Start with 0 questions
    )
    
    db.session.add(new_quiz)
    db.session.commit()

    flash("Quiz added successfully!", "success")
    return redirect(url_for("app_routes.quiz_mngmnt"))


# Update a quiz
@app_routes.route("/update_quiz/<int:id>", methods=["POST"])
def update_quiz(id):
    quiz = Quiz.query.get_or_404(id)
    quiz.name = request.form.get("quiz_name")
    quiz.time_duration = request.form.get("quiz_duration")

    db.session.commit()
    flash("Quiz updated successfully!", "success")
    return redirect(url_for("app_routes.quiz_mngmnt"))

# Delete a quiz
@app_routes.route("/delete_quiz/<int:id>", methods=["POST"])
def delete_quiz(id):
    quiz = Quiz.query.get_or_404(id)

    # Delete associated questions before deleting quiz
    Question.query.filter_by(quiz_id=id).delete()
    db.session.delete(quiz)
    db.session.commit()

    flash("Quiz deleted successfully!", "success")
    return redirect(url_for("app_routes.quiz_mngmnt"))



# Add a new question (...this updates total_qsn dynamically)
@app_routes.route("/add_question/<int:quiz_id>", methods=["POST"])
def add_question(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)

    question_title = request.form.get("question_title")
    question_statement = request.form.get("question_statement")
    option1 = request.form.get("option1")
    option2 = request.form.get("option2")
    option3 = request.form.get("option3")
    option4 = request.form.get("option4")
    correct_option = request.form.get("correct_option")

    if not all([question_title, question_statement, option1, option2, option3, option4, correct_option]):
        flash("All fields are required!", "danger")
        return redirect(url_for("app_routes.quiz_mngmnt"))

    new_question = Question(
        quiz_id=quiz_id,
        question_title=question_title,
        question_statement=question_statement,
        option1=option1,
        option2=option2,
        option3=option3,
        option4=option4,
        correct_option=correct_option,
    )

    db.session.add(new_question)
    db.session.commit()  
    quiz.total_qsn = len(quiz.questions)  
    

    db.session.commit()
    flash("Question added successfully!", "success")
    return redirect(url_for("app_routes.quiz_mngmnt"))

# Update a question
@app_routes.route("/update_question/<int:id>", methods=["POST"])
def update_question(id):
    question = Question.query.get_or_404(id)

    question.question_title = request.form.get("question_title")
    question.question_statement = request.form.get("question_statement")
    question.option1 = request.form.get("option1")
    question.option2 = request.form.get("option2")
    question.option3 = request.form.get("option3")
    question.option4 = request.form.get("option4")
    question.correct_option = request.form.get("correct_option")

    db.session.commit()
    flash("Question updated successfully!", "success")
    return redirect(url_for("app_routes.quiz_mngmnt"))

# Delete a question (updates total_qsn dynamically)
@app_routes.route("/delete_question/<int:id>", methods=["POST"])
def delete_question(id):
    question = Question.query.get_or_404(id)
    quiz = Quiz.query.get(question.quiz_id)

    db.session.delete(question)
    
    # Update total_qsn count after deleting the question
    quiz.total_qsn = Question.query.filter_by(quiz_id=quiz.id).count()

    db.session.commit()
    flash("Question deleted successfully!", "success")
    return redirect(url_for("app_routes.quiz_mngmnt"))

# user routes.......... 

@app_routes.route('/dashboard')
@login_required
def user_dashboard():
    """Fetch all available quizzes for the user."""
    quizzes = Quiz.query.order_by(Quiz.date_of_quiz.desc()).all()
    return render_template('user_dashboard.html', quizzes=quizzes)







# admin search   ...............



@app_routes.route('/admin/search', methods=['GET'])
@login_required
def admin_search():
    """Admin search functionality for users, subjects, quizzes, questions, and chapters."""

    query = request.args.get('q', '').strip().lower() 
    search_type = request.args.get('type', 'all')  

    users, subjects, quizzes, questions, chapters = [], [], [], [], []

    if query:
        # Search Users
        if search_type in ('all', 'users'):
            users = User.query.filter(
                (User.username.ilike(f"%{query}%")) | (User.email.ilike(f"%{query}%"))
            ).all()

        # Search Subjects
        if search_type in ('all', 'subjects'):
            subjects = Subject.query.filter(Subject.name.ilike(f"%{query}%")).all()

        # Search Quizzes
        if search_type in ('all', 'quizzes'):
            quizzes = Quiz.query.filter(Quiz.name.ilike(f"%{query}%")).all()

        # Search Questions
        if search_type in ('all', 'questions'):
            questions = Question.query.filter(Question.question_statement.ilike(f"%{query}%")).all()

        # Search Chapters
        if search_type in ('all', 'chapters'):
            chapters = Chapter.query.filter(Chapter.name.ilike(f"%{query}%")).all()

    return render_template(
        'admin_search.html',
        query=query,
        users=users,
        subjects=subjects,
        quizzes=quizzes,
        questions=questions,
        chapters=chapters,  
        search_type=search_type
    )

# user search.................


@app_routes.route('/user/search', methods=['GET'])
@login_required
def user_search():
    """Allows users to search for subjects, quizzes, chapters, and scores."""
    query = request.args.get('q', '').strip().lower()

    if not query:
        flash("Please enter a search term.", "warning")
        return redirect(url_for('app_routes.user_dashboard'))

    user_id = current_user.id  

    subjects = Subject.query.filter(Subject.name.ilike(f"%{query}%")).all()
    chapters = Chapter.query.filter(Chapter.name.ilike(f"%{query}%")).all()
    quizzes = Quiz.query.filter(Quiz.name.ilike(f"%{query}%")).all()
    scores = Score.query.filter_by(user_id=user_id).join(Quiz).filter(Quiz.name.ilike(f"%{query}%")).all()

    return render_template(
        "user_search.html",
        query=query,
        subjects=subjects,
        chapters=chapters,
        quizzes=quizzes,
        scores=scores
    )
#   user scores.....................



@app_routes.route('/user/scores')
@login_required
def user_scores():
    """Fetch and display user's past quiz scores categorized by subject, chapter, and quiz."""
    user_id = current_user.id  

    
    scores = (
        db.session.query(Score, Quiz, Chapter, Subject)
        .join(Quiz, Score.quiz_id == Quiz.id)
        .join(Chapter, Quiz.chapter_id == Chapter.id)
        .join(Subject, Chapter.subject_id == Subject.id)
        .filter(Score.user_id == user_id)
        .order_by(Score.id.desc())  
        .all()
    )

    return render_template("user_scores.html", scores=scores)

# user summary.......................



@app_routes.route('/user/summary')
@login_required
def user_summary():
    """Generates user quiz summary with statistics and Matplotlib charts."""
    user_id = current_user.id  

    total_quizzes = Score.query.filter_by(user_id=user_id).count()
    avg_score = db.session.query(db.func.avg(Score.total_score)).filter(Score.user_id == user_id).scalar() or 0

    subject_data = (
        db.session.query(Subject.name, db.func.count(Score.id))
        .join(Chapter, Subject.id == Chapter.subject_id)
        .join(Quiz, Chapter.id == Quiz.chapter_id)
        .join(Score, Quiz.id == Score.quiz_id)
        .filter(Score.user_id == user_id)
        .group_by(Subject.name)
        .all()
    )
    
    score_data = (
        db.session.query(Score.timestamp_of_attempt, Score.total_score)
        .filter(Score.user_id == user_id)
        .order_by(Score.timestamp_of_attempt)
        .all()
    )

    score_extremes = (
        db.session.query(Quiz.name, db.func.max(Score.total_score), db.func.min(Score.total_score))
        .join(Score, Quiz.id == Score.quiz_id)
        .filter(Score.user_id == user_id)
        .group_by(Quiz.name)
        .all()
    )

  
    subject_labels, subject_counts = zip(*subject_data) if subject_data else ([], [])
    fig, ax = plt.subplots(figsize=(6, 5))
    if subject_labels:
        ax.pie(subject_counts, labels=subject_labels, autopct='%1.1f%%', colors=['#ff9999','#66b3ff','#99ff99','#ffcc99'])
        ax.set_title("Quiz Attempts Per Subject")
    else:
        ax.text(0.5, 0.5, "No Data Available", ha='center', va='center', fontsize=12)
    
    img1 = io.BytesIO()
    plt.savefig(img1, format='png', bbox_inches='tight')
    img1.seek(0)
    subject_chart = base64.b64encode(img1.getvalue()).decode()
    plt.close()

    timestamps, scores = zip(*score_data) if score_data else ([], [])
    fig, ax = plt.subplots(figsize=(10, 5))
    if timestamps:
        ax.plot(timestamps, scores, marker='o', linestyle='-', color='#66b3ff')
        ax.set_xlabel("Date")
        ax.set_ylabel("Score")
        ax.set_title("Quiz Scores Over Time")
    else:
        ax.text(0.5, 0.5, "No Data Available", ha='center', va='center', fontsize=12)

    img2 = io.BytesIO()
    plt.savefig(img2, format='png', bbox_inches='tight')
    img2.seek(0)
    score_chart = base64.b64encode(img2.getvalue()).decode()
    plt.close()

    quiz_labels, high_scores, low_scores = zip(*score_extremes) if score_extremes else ([], [], [])
    fig, ax = plt.subplots(figsize=(6, 4))
    if quiz_labels:
        x = range(len(quiz_labels))
        ax.bar(x, high_scores, color='green', alpha=0.6, label="High Scores")
        ax.bar(x, low_scores, color='red', alpha=0.6, label="Low Scores")
        ax.set_xticks(x)
        ax.set_xticklabels(quiz_labels, rotation=45, ha='right')
        ax.set_ylabel("Scores")
        ax.set_title("Highest & Lowest Scores Per Quiz")
        ax.legend()
    else:
        ax.text(0.5, 0.5, "No Data Available", ha='center', va='center', fontsize=12)

    img3 = io.BytesIO()
    plt.savefig(img3, format='png', bbox_inches='tight')
    img3.seek(0)
    extremes_chart = base64.b64encode(img3.getvalue()).decode()
    plt.close()

    return render_template("user_summary.html", 
                           total_quizzes=total_quizzes, 
                           avg_score=round(avg_score, 2), 
                           subject_chart=subject_chart, 
                           score_chart=score_chart, 
                           extremes_chart=extremes_chart)



@app_routes.route('/admin/summary')
@login_required
def admin_summary():
    """Generates an admin dashboard summary with Matplotlib charts."""
    
    # Ensure only admin can access
    if not current_user.is_admin:
        flash("Unauthorized access!", "danger")
        return redirect(url_for('app_routes.user_dashboard'))

    total_users = User.query.count()
    total_quizzes = Quiz.query.count()
    total_questions = Question.query.count()

    # Most attempted quizzes
    quiz_attempts = (
        db.session.query(Quiz.name, db.func.count(Score.id))
        .join(Score, Quiz.id == Score.quiz_id)
        .group_by(Quiz.name)
        .order_by(db.func.count(Score.id).desc())
        .limit(5)
        .all()
    )

    # Subject-wise quiz attempts
    subject_attempts = (
        db.session.query(Subject.name, db.func.count(Score.id))
        .join(Chapter, Subject.id == Chapter.subject_id)
        .join(Quiz, Chapter.id == Quiz.chapter_id)
        .join(Score, Quiz.id == Score.quiz_id)
        .group_by(Subject.name)
        .all()
    )

    # Highest & Lowest Scores Per Quiz
    score_extremes = (
        db.session.query(Quiz.name, db.func.max(Score.total_score), db.func.min(Score.total_score))
        .join(Score, Quiz.id == Score.quiz_id)
        .group_by(Quiz.name)
        .all()
    )

    def plot_to_base64():
        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        return base64.b64encode(img.getvalue()).decode()

    plt.figure(figsize=(7, 7))
    plt.bar([q[0] for q in quiz_attempts], [q[1] for q in quiz_attempts], color='blue')
    plt.xlabel("Quiz Name")
    plt.ylabel("Attempts")
    plt.title("Most Attempted Quizzes")
    plt.xticks(rotation=30)
    quiz_attempts_chart = plot_to_base64()
    plt.close()

    plt.figure(figsize=(7, 7))
    plt.pie([s[1] for s in subject_attempts], labels=[s[0] for s in subject_attempts], autopct='%1.1f%%', colors=['red', 'blue', 'green', 'orange', 'purple'])
    plt.title("Quiz Attempts Per Subject")
    subject_attempts_chart = plot_to_base64()
    plt.close()

    plt.figure(figsize=(6, 6))
    quizzes = [s[0] for s in score_extremes]
    high_scores = [s[1] for s in score_extremes]
    low_scores = [s[2] for s in score_extremes]
    plt.bar(quizzes, high_scores, color='green', label="Highest Score")
    plt.bar(quizzes, low_scores, color='red', label="Lowest Score")
    plt.xlabel("Quiz Name")
    plt.ylabel("Scores")
    plt.title("Highest & Lowest Scores Per Quiz")
    plt.legend()
    plt.xticks(rotation=30)
    extremes_chart = plot_to_base64()
    plt.close()

    return render_template("admin_summary.html",
                           total_users=total_users,
                           total_quizzes=total_quizzes,
                           total_questions=total_questions,
                           quiz_attempts_chart=quiz_attempts_chart,
                           subject_attempts_chart=subject_attempts_chart,
                           extremes_chart=extremes_chart)

# user_quiz routes...............


from datetime import datetime, timedelta
from flask import session

@app_routes.route('/quiz_page/<int:quiz_id>/<int:q_index>')
def quiz_page(quiz_id, q_index):
    quiz = Quiz.query.get(quiz_id)
    
    if 'quiz_start_time' not in session:
        session['quiz_start_time'] = datetime.now().isoformat()

    start_time = datetime.fromisoformat(session['quiz_start_time'])
    end_time = start_time + timedelta(minutes=quiz.time_duration)
    remaining_time = (end_time - datetime.now()).total_seconds()

    if remaining_time <= 0:
        return redirect(url_for('app_routes.submit_quiz', quiz_id=quiz.id))

    question = Question.query.filter_by(quiz_id=quiz_id).offset(q_index).first()

    return render_template(
        'quiz_page.html', quiz=quiz, question=question, q_index=q_index, 
        remaining_time=int(remaining_time)
    )

@app_routes.route('/start_quiz/<int:quiz_id>')
@login_required
def start_quiz(quiz_id):
    """Redirects user to the quiz page."""
    quiz = Quiz.query.get_or_404(quiz_id)

    return redirect(url_for('app_routes.quiz_page', quiz_id=quiz.id,q_index=0))



@app_routes.route('/quiz/<int:quiz_id>/<int:q_index>/navigate', methods=['POST'])
def navigate_question(quiz_id, q_index):
    """Handles moving to the next, previous question, or submitting the quiz."""
    
    direction = request.form.get("direction")  
    total_questions = Question.query.filter_by(quiz_id=quiz_id).count()

    if direction == "next":
        next_q_index = min(q_index + 1, total_questions - 1)
    elif direction == "prev":
        next_q_index = max(q_index - 1, 0)  
    elif direction == "submit":
        return redirect(url_for('app_routes.submit_quiz', quiz_id=quiz_id))  
    else:
        next_q_index = q_index  # Stay on current question if something unexpected happens

    return redirect(url_for('app_routes.quiz_page', quiz_id=quiz_id, q_index=next_q_index))

@app_routes.route('/quiz/<int:quiz_id>/submit', methods=['GET'])
@login_required
def submit_quiz(quiz_id):
    """Submits quiz, calculates score, and stores result."""
    quiz = Quiz.query.get_or_404(quiz_id)
    user_id = current_user.id  

    responses = session.get('quiz_responses', {})

    # Ensure quiz wasn't already submitted
    # existing_score = Score.query.filter_by(user_id=user_id, quiz_id=quiz_id).first()
    # if existing_score:
    #     flash("You've already submitted this quiz.", "info")
    #     return redirect(url_for('app_routes.user_dashboard'))

    question_ids = [int(q_id) for q_id in responses.keys()]
    questions = Question.query.filter(Question.id.in_(question_ids)).all()

    question_dict = {q.id: q.correct_option for q in questions}

    score = sum(1 for q_id, selected_option in responses.items() if question_dict.get(int(q_id)) == selected_option)

    new_score = Score(user_id=user_id, quiz_id=quiz_id, total_score=score)
    db.session.add(new_score)
    db.session.commit()

    session.pop('quiz_responses', None)
    session.pop('quiz_start_time', None)

    flash(f"Quiz submitted! Your score: {score}/{quiz.total_qsn}", "success")
    return redirect(url_for('app_routes.user_dashboard'))
