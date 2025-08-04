# app/auth.py

import os
from flask_login import LoginManager, UserMixin

login_manager = LoginManager()
login_manager.login_view = "main.login" # Note: endpoint is now blueprint_name.function_name

class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

# Load user from .env
app_user = User(
    id=1, 
    username=os.getenv("APP_USERNAME"), 
    password=os.getenv("APP_PASSWORD")
)

@login_manager.user_loader
def load_user(user_id):
    if int(user_id) == app_user.id:
        return app_user
    return None