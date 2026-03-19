"""Configuration settings for Separation PMO."""
import os

# Resolve project root for reliable SQLite path
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_default_db = 'sqlite:///' + os.path.join(_project_root, 'instance', 'separation_pmo.db').replace('\\', '/')


class Config:
    """Base configuration."""
    APP_NAME = "Separation PMO"
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

    # Database
    database_url = os.environ.get('DATABASE_URL', _default_db)
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    SQLALCHEMY_DATABASE_URI = database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Claude AI
    ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
    CLAUDE_MODEL = os.environ.get('CLAUDE_MODEL', 'claude-sonnet-4-20250514')

    # Rate limiting
    RATELIMIT_DEFAULT = "100 per minute"

    # Upload
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
