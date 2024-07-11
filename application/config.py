class Config:
    SECRET_KEY = 'hard to guess string' 
    SQLALCHEMY_DATABASE_URI = 'sqlite:///data.sqlite3'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    DEBUG = True