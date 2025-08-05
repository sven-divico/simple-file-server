# app/api.py
import os
import hmac
from functools import wraps
from flask import Blueprint, request, jsonify, send_from_directory, abort, current_app
from werkzeug.utils import secure_filename

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

# --- NEW: Feature Flag Decorator ---
def feature_enabled(config_key):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_app.config.get(config_key, False):
                abort(403, description=f"This feature ({config_key}) is disabled by the server administrator.")
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def api_key_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Use the new key name
        api_key = current_app.config.get("FILE_SERVER_API_KEY") 
        provided_key = request.headers.get('X-API-Key')
        if not api_key:
            abort(500, description="API key not configured on the server.")
        if not provided_key or not hmac.compare_digest(api_key, provided_key):
            abort(401, description="Invalid or missing API Key.")
        return f(*args, **kwargs)
    return decorated_function

# --- NEW: Health Check Endpoint ---
@api_bp.route('/health', methods=['GET'])
def health_check():
    """Provides a health check for the service."""
    mode = current_app.config.get('HEALTH_CHECK_MODE', 'simple')
    if mode == 'debug':
        # WARNING: This exposes configuration and should not be used in production.
        config_data = {
            "status": "ok",
            "health_check_mode": mode,
            "enabled_features": {
                "uploads": current_app.config['ENABLE_FILE_UPLOADS'],
                "downloads": current_app.config['ENABLE_FILE_DOWNLOADS'],
                "deletions": current_app.config['ENABLE_FILE_DELETION'],
                "public_url_downloads": current_app.config['ENABLE_HTTP_URL_DOWNLOADS'],
            }
        }
        return jsonify(config_data), 200
    
    # Default simple mode
    return jsonify({"status": "ok"}), 200


# We use the full docstrings from before, I'm omitting them here for brevity
@api_bp.route('/upload', methods=['POST'])
@api_key_required
@feature_enabled('ENABLE_FILE_UPLOADS') # toggle for enabling file uploads
def upload_file_api():
    """Upload one or more files... (full docstring here)"""
    DOCUMENT_ROOT = current_app.config["DOCUMENT_ROOT"]
    if 'files' not in request.files:
        abort(400, description="No file part in the request")
    files = request.files.getlist('files')
    uploaded_files = []
    for file in files:
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            file.save(os.path.join(DOCUMENT_ROOT, filename))
            uploaded_files.append(filename)
    if not uploaded_files:
        abort(400, description="No files were selected for upload")
    return jsonify(message=f"Successfully uploaded {len(uploaded_files)} file(s)", uploaded_files=uploaded_files), 201

@api_bp.route('/files', methods=['GET'])
@api_key_required
@feature_enabled('ENABLE_FILE_DOWNLOADS')
def list_files_api():
    """Lists all files in the document root."""
    DOCUMENT_ROOT = current_app.config["DOCUMENT_ROOT"]
    try:
        # Create a list of files, excluding any subdirectories
        files = [f for f in os.listdir(DOCUMENT_ROOT) if os.path.isfile(os.path.join(DOCUMENT_ROOT, f))]
        files.sort() # Sort the list alphabetically for consistent output
        return jsonify({"files": files}), 200
    except FileNotFoundError:
        # If the root directory doesn't exist, return an empty list.
        # This is a graceful way to handle the error for the client.
        return jsonify({"files": []}), 200
    except Exception as e:
        # Catch other potential errors (e.g., permissions)
        abort(500, description=f"Could not read directory: {e}")

@api_bp.route('/files/<path:filename>')
@api_key_required
def serve_file_api(filename):
    """Download a specific file... (full docstring here)"""
    return send_from_directory(current_app.config["DOCUMENT_ROOT"], filename)

@api_bp.route('/delete/<path:filename>', methods=['POST'])
@api_key_required
@feature_enabled('ENABLE_FILE_DELETION')
def delete_file_api(filename):
    """Delete a specific file... (full docstring here)"""
    DOCUMENT_ROOT = current_app.config["DOCUMENT_ROOT"]
    try:
        safe_filename = secure_filename(filename)
        file_path = os.path.join(DOCUMENT_ROOT, safe_filename)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            os.remove(file_path)
            return jsonify(message=f'File "{safe_filename}" deleted successfully.'), 200
        else:
            abort(404, description=f'File "{safe_filename}" not found.')
    except Exception as e:
        abort(500, description=f'Error deleting file: {e}')