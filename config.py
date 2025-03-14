import os


class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here')
    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'
    DEBUG = False
    TESTING = False

    # Application settings
    APP_NAME = 'HealthPredict'
    APP_DESCRIPTION = 'AI-powered health prediction platform'
    ADMIN_EMAIL = 'admin@healthpredict.ai'

    # Model settings
    MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models')
    DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    DATABASE_URI = 'sqlite:///dev.db'


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True
    DATABASE_URI = 'sqlite:///test.db'


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///prod.db')
    # In a production environment, use a proper secret key
    SECRET_KEY = os.environ.get('SECRET_KEY', os.urandom(24).hex())


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config():
    """Get the configuration based on environment variable."""
    env = os.environ.get('FLASK_ENV', 'default')
    return config.get(env, config['default'])