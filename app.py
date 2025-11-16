# Replit Auth Blueprint - Flask app initialization
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy.orm import DeclarativeBase
import os
from werkzeug.middleware.proxy_fix import ProxyFix
import logging
from flask_login import LoginManager
from db_service import get_db, User as MongoUser
# Configure logging
logging.basicConfig(level=logging.DEBUG)


# Initialize Flask app
app = Flask(__name__, static_folder='client/dist', static_url_path='')
app.secret_key = os.environ.get("SESSION_SECRET", "super_secret_key_123")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# CORS configuration
CORS(app, supports_credentials=True, origins=["*"])

login_manager = LoginManager(app)
login_manager.login_view = 'auth.google_login' 
login_manager.login_message = "Vui lòng đăng nhập để truy cập trang này."

@login_manager.user_loader
def load_user(user_id):
    """Tải user từ database dựa trên user_id."""
    user_data = get_db().users.find_one({"_id": user_id})
    if user_data:
        return MongoUser(user_data)
    return None

try:
    from db_service import get_db
    get_db() # Thử kết nối
    logging.info("MongoDB connection for user data successful.")
except Exception as e:
    logging.error(f"MongoDB connection failed: {e}")