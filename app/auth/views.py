"""
Модуль представлений для аутентификации.

В этом модуле содержатся представления, связанные с аутентификацией
пользователей, такие как вход, регистрация, выход, подтверждение аккаунта
и неподтвержденный доступ. Также здесь определены вспомогательные функции
для отправки писем подтверждения и асинхронной отправки электронных писем.
"""

from flask import render_template, redirect, request, flash, url_for
from flask_mail import Message
from app.auth import auth
from app.auth.forms import LoginForm, RegistrationForm
from app import db, mail
from app.models import User, Role
from flask_login import login_user, login_required, logout_user, current_user
from threading import Thread


@auth.before_app_request
def before_request():
    """
    Функция, выполняемая перед каждым запросом к приложению.

    Если пользователь аутентифицирован и не подтвержден,
    и текущий запрос не относится к разделу аутентификации,
    то происходит перенаправление на страницу неподтвержденных пользователей.
    """
    if current_user.is_authenticated:
        current_user.ping()
        if current_user.is_authenticated and not current_user.confirmed and request.blueprint != 'auth' and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))


@auth.route('/login', methods=['GET', 'POST'])
def login():
    """
    Представление для входа пользователя в систему.

    Если форма валидна и аутентификация успешна,
    происходит вход пользователя в систему.
    В случае неудачи выводится сообщение об ошибке.
    """
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.password_verify(form.password.data):
            login_user(user)
            next = request.args.get("next")
            if next is None or not next.startswith('/'):
                next = url_for('main.home')
            return redirect(next)
        flash('Invalid email or password')
    return render_template("auth/login.html", form=form)


@auth.route("/register", methods=["GET", "POST"])
def register():
    """
    Представление для регистрации нового пользователя.

    Если форма валидна, создается новый пользователь в базе данных
    с использованием данных, введенных в форму.
    После успешной регистрации происходит перенаправление на страницу входа.
    """
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, username=form.username.data, name=form.name.data,
                    role=Role.query.get(form.role.data))
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_confirm(user, token)
        flash('Вам отправлено письмо для подтверждения аккаунта.')
        return redirect(url_for('auth.login'))
    return render_template("auth/registration.html", form=form)


@auth.route("/logout")
@login_required
def logout():
    """
    Представление для выхода пользователя из системы.

    После выхода из системы происходит перенаправление на главную страницу.
    """
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for('main.home'))


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    """
    Представление для подтверждения аккаунта пользователя.

    Если пользователь уже подтвержден, происходит перенаправление на главную страницу.
    Если подтверждение прошло успешно, происходит перенаправление на страницу входа.
    В противном случае выводится сообщение об ошибке.
    """
    print(token)
    if current_user.confirmed:
        return redirect(url_for('main.home'))
    if current_user.confirm(token):
        db.session.commit()
        flash("Подтверждено")
        return redirect(url_for('auth.login'))
    else:
        flash("Ссылка не работает")
    return redirect(url_for('main.home'))


@auth.route('/unconfirmed')
def unconfirmed():
    """
    Представление для отображения страницы неподтвержденных пользователей.

    Если пользователь анонимный или уже подтвержден,
    происходит перенаправление на главную страницу.
    """
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.home'))
    return render_template('auth/unconfirmed.html')


def send_confirm(user, token):
    """
    Функция для отправки электронного письма для подтверждения аккаунта.

    :param user: Пользователь, которому отправляется письмо.
    :param token: Токен подтверждения.
    """
    confirm_url = url_for('auth.confirm', token=token, _external=True)
    send_mail(user.email, 'Подтвердите свою учетную запись',
              'auth/confirm', user=user, confirm_url=confirm_url)


def send_mail(to, subject, template, **kwargs):
    """
    Функция для отправки электронного письма.

    :param to: Получатель письма.
    :param subject: Тема письма.
    :param template: Шаблон для формирования письма.
    :param **kwargs: Дополнительные аргументы для формирования письма.
    """
    msg = Message(
        subject, sender="elena.zavadskaya111@gmail.com", recipients=[to])
    try:
        msg.html = render_template(template + ".html", **kwargs)
    except:
        msg.body = render_template(template + ".txt", **kwargs)
    from app_file import flask_app
    thread = Thread(target=send_async_email, args=[flask_app, msg])
    thread.start()
    return thread


def send_async_email(app, msg):
    """
    Функция для асинхронной отправки электронного письма.

    :param app: Flask-приложение.
    :param msg: Объект сообщения.
    """
    with app.app_context():
        mail.send(msg)
