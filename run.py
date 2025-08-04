# run.py
from app import create_app
import os

app = create_app()

if __name__ == '__main__':
    # Ensure the document root directory exists
    os.makedirs(app.config['DOCUMENT_ROOT'], exist_ok=True)
    app.run(host='0.0.0.0', port=5000, debug=True)