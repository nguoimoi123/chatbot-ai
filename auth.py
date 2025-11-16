from flask import Blueprint, redirect, url_for, session
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.contrib.github import make_github_blueprint, github
from flask_login import login_user
from db_service import find_user_by_email, save_user
import os

auth_bp = Blueprint("auth", __name__)

# --- GOOGLE LOGIN ---
google_bp = make_google_blueprint(
    client_id=os.getenv("GOOGLE_OAUTH_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_OAUTH_CLIENT_SECRET"),
    scope=[
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/userinfo.email",
        "openid"
    ],
    redirect_to="auth.google_login"
)

# --- GITHUB LOGIN ---
github_bp = make_github_blueprint(
    client_id=os.getenv("GITHUB_OAUTH_CLIENT_ID"),
    client_secret=os.getenv("GITHUB_OAUTH_CLIENT_SECRET"),
    scope="user:email",
    redirect_to="auth.github_login"
)

@auth_bp.route("/login/google")
def google_login():
    if not google.authorized:
        return redirect(url_for("google.login"))
    
    resp = google.get("/oauth2/v2/userinfo")
    if not resp.ok:
        return redirect(url_for("google.login"))
        
    user_info = resp.json()

    user = find_user_by_email(user_info["email"])
    
    if not user:
        user = save_user(user_info)
    
    login_user(user)
    next_url = session.pop("next_url", "/")
    return redirect(next_url)

@auth_bp.route("/login/github")
def github_login():
    if not github.authorized:
        return redirect(url_for("github.login"))
    
    resp = github.get("/user")
    if not resp.ok:
        return redirect(url_for("github.login"))

    user_info = resp.json()
    email = user_info.get("email")
    if not email:
        email_resp = github.get("/user/emails")
        if email_resp.ok:
            emails = email_resp.json()
            primary_email = next((e['email'] for e in emails if e['primary'] and e['verified']), None)
            email = primary_email

    if not email:
        return "Không thể lấy email từ tài khoản GitHub của bạn.", 400

    user = find_user_by_email(email)
    if not user:
        user_info['email'] = email
        user = save_user(user_info)

    login_user(user)
    next_url = session.pop("next_url", "/")
    return redirect(next_url)