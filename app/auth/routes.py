from flask import render_template, redirect, url_for, flash, request
from urllib.parse import urlparse
from flask_login import current_user, login_user, logout_user
from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegisterForm, ResetPasswordForm, ResetPasswordRequestForm
from app.models import User
from app.auth.email import send_password_reset_mail


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('auth.index'))

    forms = LoginForm()
    if forms.validate_on_submit():
        user = User.query.filter_by(username=forms.username.data).first()
        if user is None or not user.check_password(forms.password.data):
            flash('Invalid Username or Password')
            return redirect(url_for('auth.login'))

        login_user(user, remember=forms.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('auth.index')
        return redirect(next_page)

    return render_template('auth/login.html', title='Sign In', form=forms)


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('auth.index'))

    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('User Signup Successful, Login to continue')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title='Signup', form=form)


@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('auth.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_mail(user)
        flash('Check your mail to reset your password !')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html', title='Password Reset Request', form=form)


@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('auth.index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('auth.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Password has been reset.')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', title='Password Reset', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.index'))
