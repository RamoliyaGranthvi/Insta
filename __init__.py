# app/__init__.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from model import db
from flask_restful import Api
from endpoints import add_routes  # Import your API route handlers
from config import DevelopmentConfig


def create_app(config_class=DevelopmentConfig):
    # Initialize the Flask app
    app = Flask ( __name__ )

    # Load configuration
    app.config.from_object ( config_class )

    # Initialize the database and migration object
    db.init_app ( app )

    # Initialize the API
    api = Api ( app )

    # Register your routes (assumes `add_routes` is a function in endpoints.py that sets up API routes)
    add_routes ( api )

    return app
