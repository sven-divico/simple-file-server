# app/__init__.py

import os
from flask import Flask, request, jsonify, render_template
from werkzeug.exceptions import HTTPException
from flasgger import Swagger
from dotenv import load_dotenv
from .auth import login_manager # We'll create auth.py in a moment

def create_app():
    # Load env variables at the very top
    load_dotenv(dotenv_path='../.env')

    # The __name__ now points to the 'app' package
    app = Flask(__name__)

    # --- Configuration ---
    
    # --- Helper function to parse boolean env vars ---
    def str_to_bool(s):
        return s.lower() in ['true', '1', 't', 'y', 'yes']

    # --- Configuration ---
    app.config['SECRET_KEY'] = os.getenv("FLASK_SECRET_KEY")
    app.config['DOCUMENT_ROOT'] = os.getenv("DOCUMENT_ROOT", "/data")
    app.config['FILE_SERVER_API_KEY'] = os.getenv("FILE_SERVER_API_KEY") # <-- Renamed
    
    # Load new feature flags
    app.config['ENABLE_FILE_UPLOADS'] = str_to_bool(os.getenv("ENABLE_FILE_UPLOADS", "true"))
    app.config['ENABLE_FILE_DOWNLOADS'] = str_to_bool(os.getenv("ENABLE_FILE_DOWNLOADS", "true"))
    app.config['ENABLE_FILE_DELETION'] = str_to_bool(os.getenv("ENABLE_FILE_DELETION", "true"))
    app.config['ENABLE_HTTP_URL_DOWNLOADS'] = str_to_bool(os.getenv("ENABLE_HTTP_URL_DOWNLOADS", "true"))
    app.config['HEALTH_CHECK_MODE'] = os.getenv("HEALTH_CHECK_MODE", "simple").lower()

    # --- Initialize Extensions ---
    login_manager.init_app(app)
    Swagger(app, template_file='../apidocs.yaml') # We'll create this file

    # --- Register Blueprints ---
    from .main import main_bp
    app.register_blueprint(main_bp)

    from .api import api_bp
    app.register_blueprint(api_bp)

    # --- Centralized Error Handler ---
    @app.errorhandler(HTTPException)
    def handle_exception(e):
        if request.path.startswith('/api/'):
            response = e.get_response()
            response.data = jsonify({ "code": e.code, "name": e.name, "description": e.description, }).data
            response.content_type = "application/json"
            return response
        if e.code == 404:
            return render_template("404.html"), 404
        return e

    return app