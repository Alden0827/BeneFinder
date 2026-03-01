import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    AUTH_API_URL = os.environ.get('AUTH_API_URL')
    AUTH_API_KEY = os.environ.get('AUTH_API_KEY')
    AUTH_API_VERIFY_SSL = os.environ.get('AUTH_API_VERIFY_SSL', 'False') == 'True'
    APP_NAME = os.environ.get('APP_NAME', 'Pantawid Beneficiary Search & Verification')
    DEV_CONTACT = os.environ.get('DEV_CONTACT', 'aaquinones.fo12@dswd.gov.ph')
