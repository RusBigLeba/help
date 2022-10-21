import os
import json
import requests
from flask import (
	Blueprint, flash, redirect, render_template, 
	request, url_for, send_from_directory
)
from flask_login import login_user, logout_user, current_user, login_required
from buildyourownbotnet import client, c2
from buildyourownbotnet.core.dao import user_dao
from buildyourownbotnet.users.forms import RegistrationForm, LoginForm, UpdateAccountForm, ResetPasswordForm
from buildyourownbotnet.models import db, bcrypt, User, Session


# Blueprint
users = Blueprint('users', __name__)

# Globals
OUTPUT_DIR = os.path.abspath('buildyourownbotnet/output')


# Routes

@users.route("/login", methods=['GET', 'POST'])
def login():
	"""Log user in"""
	if current_user.is_authenticated:
		return redirect(url_for('main.sessions'))

	form = LoginForm()
	if form.validate_on_submit():
		user = user_dao.get_user(username=form.username.data)
		if user and bcrypt.check_password_hash(user.password, form.password.data):
			login_user(user)
			next_page = request.args.get('next')
			return redirect(next_page) if next_page else redirect(url_for('main.sessions'))
		flash("Invalid username/password.", 'danger')
	return render_template("login.html", form=form, title="Log In"), 403


@users.route("/account", methods=['GET','POST'])
@login_required
def account():
	"""Account configuration page."""
	form = ResetPasswordForm()
	if form.validate_on_submit():

		# update user's password in the database
		user = User.query.filter_by(username=current_user.username).first()
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user.password = hashed_password
		db.session.commit()
		flash("Your password has been updated.", "success")
		db.session.commit()
	return render_template("account.html", 
							title="Account",
							form=form)


@users.route('/logout')
@login_required
def logout():
	"""Log out"""
	logout_user()
	return render_template("home.html")
