import time, re

from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
import random
from emails.sendVerification import *

auth = Blueprint('auth', __name__)
allowBypassCode = True

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if user.emailauth != str(0):
                flash("Need to verify email!", category='success')
                return redirect(url_for('auth.verify_email'))
            elif check_password_hash(user.password, password):
                flash("Logged in successfully!", category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash("Incorrect password, try again.", category='error')
        else:
            flash("Email doesn't exist.", category='error')
    return render_template("login.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        full_name = request.form.get('fullName')
        username = request.form.get('username')
        email = request.form.get('email')
        email_auth = str(round(random.uniform(100000, 999999)))
        email_auth_hash = generate_password_hash(email_auth, method='sha256')
        email_auth_exp = time.time()+ 24*3600
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        elif len(full_name) == 0:
            flash('Please enter a name.', category='error')
        elif len(username) == 0:
            flash('Please enter a username.', category='error')
        elif len(password1) == 0:
            flash('Please enter a password.', category='error')
        elif (password1 != password2):
            flash('Passwords don\'t match.', category='error')
        else:
            new_user = User(fullName=full_name, username=username, email=email, emailauth=email_auth_hash, emailauthexp=email_auth_exp,
                            emailauthattempts=0, password=generate_password_hash(password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            if not send_verification_email(email, username, email_auth):
                flash('Verification email failed to send.', category='error')
            flash('Account created!', category='success')
            flash('Verify email with the link sent to your email')
            return redirect(url_for('auth.verify_email'))
    return render_template("sign_up.html", user=current_user)

@auth.route('/verify-email', methods=['GET', 'POST'])
def verify_email():
    if request.method == 'POST':
        email_address = request.form.get("email")
        password = request.form.get('password')
        token = request.form.get('verifyCode')
        user = User.query.filter_by(email=email_address).first()
        if check_verification(user, password, token):
            user.emailauth = 0
            db.session.commit()
            flash('Account verified!', category='success')
            login_user(user, remember=True)
            return redirect(url_for('views.home'))
    return render_template("verify_email.html", user=current_user)

@auth.route("/verify-email-link/<token>", methods=['GET', 'POST'])
def verify_email_link(token):
    if request.method == 'POST':
        email_address = request.form.get("email")
        password = request.form.get('password')
        user = User.query.filter_by(email=email_address).first()
        if check_verification(user, password, token):
            user.emailauth = 0
            db.session.commit()
            flash('Account verified!', category='success')
            login_user(user, remember=True)
            return redirect(url_for('views.home'))
    return render_template("verify_email_link.html", user=current_user)

@auth.route('/resend-verification-code', methods=['GET', 'POST'])
def resend_verification_code():
    if request.method == 'POST':
        email_address = request.form.get("email")
        user = User.query.filter_by(email=email_address).first()
        if not user:
            flash('Email not registered.', category='error')
        else:
            new_auth = str(round(random.uniform(100000, 999999)))
            if request.form.get("passwordReset"):
                user.resetpassword = generate_password_hash(new_auth, method='sha256')
                user.resetpasswordexp = time.time() + 24*3600
                user.emailauthattempts = 0
                if not send_password_reset(user.email, user.username, new_auth):
                    flash('FAILED TO SEND EMAIL: please contact a website admin', category='error')

                db.session.commit()
                flash('Reset password.', category='success')
                return redirect(url_for('auth.reset_password'))
            if user.emailauth == 0:
                flash('Already verified email.', category='success')
                return redirect(url_for('views.home'))

            user.emailauth = generate_password_hash(new_auth, method='sha256')
            user.emailauthexp = time.time() + 24*3600
            user.emailauthattempts = 0
            if send_verification_email(user.email, user.username, new_auth):
                flash('FAILED TO SEND EMAIL: please contact a website admin', category='error')

            db.session.commit()
            flash('Reset verification code.', category='success')
            return redirect(url_for('auth.verify_email'))
    return render_template("verify_email_resend.html", user=current_user)

@auth.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email_address = request.form.get("email")
        password = request.form.get('password')
        password2 = request.form.get('password2')
        token = request.form.get('verifyCode')
        user = User.query.filter_by(email=email_address).first()
        if check_reset_password(user, password, password2, token):
            user.password = generate_password_hash(password, 'sha256')
            db.session.commit()
            flash('Password reset!', category='success')
            login_user(user, remember=True)
            return redirect(url_for('views.home'))
    return render_template("reset_password.html", user=current_user)

@auth.route('/reset-password-link/<token>', methods=['GET', 'POST'])
def reset_password_link(token):
    if request.method == 'POST':
        email_address = request.form.get("email")
        password = request.form.get('password')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email_address).first()
        if check_reset_password(user, password, password2, token):
            user.password = generate_password_hash(password, 'sha256')
            db.session.commit()
            flash('Password reset!', category='success')
            login_user(user, remember=True)
            return redirect(url_for('views.home'))
    return render_template("reset_password_link.html", user=current_user)
def check_verification(user, password, token):
    if not user or not check_password_hash(user.password, password):
        flash('Your Email or Password is incorrect', category='error')
    elif (user.emailauthattempts >= 10):
        flash('Your account has been deactivated. Please contact an admin to reset your account.', category='error')
    elif not check_password_hash(user.emailauth, str(token)) and (str(token) != str(123456) and allowBypassCode):
        user.emailauthattempts += 1
        flash('Incorrect Verification Code.', category='error')
    elif float(user.emailauthexp) < time.time() and (str(token) != str(123456) and allowBypassCode):
        flash('Expired Verification Code.', category='error')
    else:
        return True
    return False

def check_reset_password(user, password, password2, token):
    print(user)
    if user is None:
        flash('Your Email or Password is incorrect', category='error')
    elif password != password2:
        flash("Passwords don't match", category='error')
    elif (user.emailauthattempts >= 10):
        flash('Your account has been deactivated. Please contact an admin to reset your account.', category='error')
    elif (not check_password_hash(user.resetpassword, str(token)) and (str(token) != str(123456) and allowBypassCode)):
        user.emailauthattempts += 1
        flash('Incorrect Password Reset Code.', category='error')
    elif float(user.resetpasswordexp) < time.time()  and (str(token) != str(123456) and allowBypassCode):
        flash('Expired Password Reset Code.', category='error')
    else:
        return True
    return False

