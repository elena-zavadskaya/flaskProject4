from flask_mail import Message

from flask import request, make_response, render_template, redirect, url_for, session
import random

from app.main.forms import UserForm
from app.models import User

from . import main
from app import mail
from flask_login import login_required, current_user


@main.route('/')
@main.route('/home')
def set_cookie():
    session_text = session.get('text')
    if session_text is not None or session_text != "":
        return render_template("home.html")
    else:
        return render_template("home.html")


@main.route('/user/<name>')
def hello_user(name):
    return render_template('user.html', name=name, current_user=current_user)


@main.route('/secret')
@login_required
def secret():
    return "Only for auth"

@main.route("/testConfirm")
def testConfirm():
    user = User.query.filter_by().first()
    tmp = user.generate_confirmation_token()
    user.confirm(tmp)