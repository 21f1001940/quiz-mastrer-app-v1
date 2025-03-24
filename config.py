import os

# Define base directory of the project
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Application configuration
class Config:
    SECRET_KEY = "your_secret_key"  # Used for session security
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "quiz_master.db")  # SQLite database
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # To disable modification tracking (recommended)
