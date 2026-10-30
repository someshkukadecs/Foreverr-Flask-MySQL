import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

class Config:
    """
    Application configuration class.
    Reads sensitive settings from environment variables or uses sensible defaults.
    """
    # Secret key used for securely signing session cookies
    SECRET_KEY = os.environ.get('SECRET_KEY', 'foreverr-super-secret-key-2026')

    # MySQL Database Connection URL:
    # Format: mysql+pymysql://<username>:<password>@<host>/<database_name>
    # Change 'YOUR_PASSWORD' in your .env file with your actual MySQL password!
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'mysql+pymysql://root:YOUR_PASSWORD@localhost/foreverr'
    )

    # Disable tracking modifications to save memory and improve performance
    SQLALCHEMY_TRACK_MODIFICATIONS = False
