# app/main.py

import os
from flask import Blueprint, render_template, request, flash, redirect, url_for, send_from_directory, current_app
from flask_login import login_required, current_user, login_user, logout_user
from werkzeug.utils import secure_filename
from .auth import User, app_user # We'll create auth.py next

# A Blueprint is a way to organize a group of related views and other code.
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@login_required
def index():
    DOCUMENT_ROOT = current_app.config["DOCUMENT_ROOT"]
    try:
        files = [f for f in os.listdir(DOCUMENT_ROOT) if os.path.isfile(os.path.join(DOCUMENT_ROOT, f))]
        files.sort()
    except FileNotFoundError:
        files = []
        flash(f"Error: The shared directory '{DOCUMENT_ROOT}' was not found.", "error")
    return render_template('index.html', files=files)

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == app_user.username and password == app_user.password:
            login_user(app_user)
            return redirect(url_for('main.index'))
        else:
            flash('Invalid username or password', 'error')
    return render_template('login.html')

@main_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

@main_bp.route('/upload', methods=['POST'])
@login_required
def upload_file():
    DOCUMENT_ROOT = current_app.config["DOCUMENT_ROOT"]
    if 'files' not in request.files:
        flash('No file part in the request', 'error')
        return redirect(url_for('main.index'))
    files = request.files.getlist('files')
    uploaded_count = 0
    for file in files:
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            file.save(os.path.join(DOCUMENT_ROOT, filename))
            uploaded_count += 1
    if uploaded_count > 0:
        flash(f'Successfully uploaded {uploaded_count} file(s)!', 'success')
    else:
        flash('No files were selected for upload.', 'error')
    return redirect(url_for('main.index'))

@main_bp.route('/files/<path:filename>')
@login_required
def serve_file(filename):
    return send_from_directory(current_app.config["DOCUMENT_ROOT"], filename)

@main_bp.route('/delete/<path:filename>', methods=['POST'])
@login_required
def delete_file(filename):
    DOCUMENT_ROOT = current_app.config["DOCUMENT_ROOT"]
    try:
        safe_filename = secure_filename(filename)
        file_path = os.path.join(DOCUMENT_ROOT, safe_filename)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            os.remove(file_path)
            flash(f'File "{safe_filename}" deleted successfully.', 'success')
        else:
            flash(f'File "{safe_filename}" not found.', 'error')
    except Exception as e:
        flash(f'Error deleting file: {e}', 'error')
    return redirect(url_for('main.index'))
