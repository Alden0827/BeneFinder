from flask import Blueprint, render_template, redirect, url_for, flash, request, session, make_response, current_app
from flask_login import login_user, logout_user, current_user
from models import db, User
import requests
from io import BytesIO
from captcha.image import ImageCaptcha
import random
import string
from werkzeug.security import check_password_hash, generate_password_hash
from flask_bcrypt import Bcrypt

auth_bp = Blueprint('auth', __name__)
bcrypt = Bcrypt()


def generate_captcha_text(length=4):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

@auth_bp.route('/captcha')
def captcha():
    image = ImageCaptcha(width=160, height=60)
    captcha_text = generate_captcha_text()
    session['captcha'] = captcha_text
    data = image.generate(captcha_text)
    response = make_response(data.read())
    response.headers['Content-Type'] = 'image/png'
    return response

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('finder.index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        captcha_input = request.form.get('captcha')
        remember = True if request.form.get('remember') else False

        if captcha_input != session.get('captcha'):
            flash('Incorrect CAPTCHA', 'error')
            return redirect(url_for('auth.login'))

        # LDAP Authentication
        auth_url = current_app.config['AUTH_API_URL']
        auth_key = current_app.config['AUTH_API_KEY']
        verify_ssl = current_app.config['AUTH_API_VERIFY_SSL']

        try:
            # 1. Request token
            token_resp = requests.post(f"{auth_url}/request_token",
                                     json={'username': username, 'password': password},
                                     headers={'X-API-Key': auth_key},
                                     verify=verify_ssl)
            token_data = token_resp.json()

            if token_data.get('success'):
                token = token_data['token']
                # 2. Request user info
                user_info_resp = requests.post(f"{auth_url}/user_info",
                                             json={'token': token},
                                             headers={'X-API-Key': auth_key},
                                             verify=verify_ssl)
                user_info_data = user_info_resp.json()

                if user_info_data.get('success'):
                    api_user = user_info_data['user']

                    user = User.query.filter_by(username=api_user['sAMAccountName']).first()
                    if not user:
                        user = User(
                            username=api_user['sAMAccountName'],
                            firstname=api_user.get('givenName'),
                            middlename=api_user.get('initials'),
                            lastname=api_user.get('sn'),
                            email=api_user.get('email'),
                            contact=api_user.get('mobile'),
                            group_id=8,
                            status='Active',
                            password=generate_password_hash(password)
                        )
                        db.session.add(user)
                    else:
                        user.firstname = api_user.get('givenName')
                        user.lastname = api_user.get('sn')
                        user.password = generate_password_hash(password)

                    db.session.commit()
                    login_user(user, remember=remember)
                    return redirect(url_for('finder.index'))

        except Exception as e:
            print(f"LDAP Auth Error: {str(e)}")

        # Fallback to local DB auth (Keep for development/resilience unless strictly forbidden)
        user = User.query.filter_by(username=username).first()
        if user and user.password:
            try:
                if bcrypt.check_password_hash(user.password, password):
                    login_user(user, remember=remember)
                    return redirect(url_for('finder.index'))
            except ValueError:
                # Handle cases where user.password is not a valid Werkzeug hash (e.g., empty string, legacy hash)
                pass

        flash('Login failed. Please check your username and password.', 'error')

    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
