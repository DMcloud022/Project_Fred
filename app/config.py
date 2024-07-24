import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///project_analysis.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    GROQ_API_KEY = os.environ.get('GROQ_API_KEY')