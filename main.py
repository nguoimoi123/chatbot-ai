# Replit Auth Blueprint - Main entry point
from app import app
from auth import google_bp, github_bp, auth_bp
import routes  # noqa: F401
import logging


app.register_blueprint(google_bp, url_prefix="/login")
app.register_blueprint(github_bp, url_prefix="/login")
app.register_blueprint(auth_bp, url_prefix="/auth")

if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=3000, debug=True)

# logging.getLogger('pymongo').setLevel(logging.ERROR)
# logging.getLogger("urllib3").setLevel(logging.WARNING)
# logging.getLogger('flask').setLevel(logging.WARNING)
# logging.getLogger().setLevel(logging.WARNING)
    pass