import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database
DATABASE_NAME = "Fyyur"
class DatabaseURI:
    
    username = 'zhu'
    password = ''
    url = 'localhost:5432'
    address = "postgresql://{}:{}@{}/{}".format(
        username, password, url, DATABASE_NAME)

# IMPLEMENT DATABASE URL
SQLALCHEMY_DATABASE_URI = DatabaseURI.address
SQLALCHEMY_TRACK_MODIFICATIONS = False