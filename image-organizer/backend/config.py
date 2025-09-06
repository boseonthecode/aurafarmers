import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    UPLOAD_FOLDER = '../uploads'
    ORGANIZED_FOLDER = '../uploads/organized'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size