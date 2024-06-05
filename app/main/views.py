from flask import render_template, session, request, flash, redirect, url_for
from app.models import User, Permission, Book, UserLibrary, News
from .. import db
from ..auth.forms import NewsForm
from ..decorators import admin_required, permission_required
from . import main
from flask_login import login_required, current_user
import requests


@main.route('/user_library')
@login_required
def user_library():
    books = UserLibrary.query.filter_by(user_id=current_user.id).all()
    return render_template('user_library.html', books=books)


@main.route('/', methods=['GET', 'POST'])
@main.route('/home', methods=['GET', 'POST'])
def home():
    search_query = request.form.get('search')
    search_results = []
    if search_query:
        response = requests.get(f'https://www.googleapis.com/books/v1/volumes?q={search_query}')
        if response.status_code == 200:
            data = response.json()
            search_results = data.get('items', [])

    news_list = News.query.order_by(News.timestamp.desc()).all()
    return render_template('home.html', search_results=search_results, news_list=news_list)


@main.route('/add_news', methods=['GET', 'POST'])
@login_required
def add_news():
    if not current_user.is_admin():
        flash('Доступ запрещен.')
        return redirect(url_for('main.home'))
    if request.method == 'POST':
        title = request.form.get('title')
        image = request.form.get('image')
        description = request.form.get('description')
        content = request.form.get('content')
        if title and content:
            news = News(
                title=title,
                image=image,
                description=description,
                content=content,
                author=current_user  # Убедитесь, что автор присваивается здесь
            )
            db.session.add(news)
            db.session.commit()
            flash('Новость добавлена.')
            return redirect(url_for('main.home'))
        else:
            flash('Заполните все обязательные поля.')
    return render_template('add_news.html')


@main.route('/news/<int:news_id>')
def news_detail(news_id):
    news = News.query.get_or_404(news_id)
    return render_template('news_detail.html', news=news)


@main.route('/edit_news/<int:news_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_news(news_id):
    news = News.query.get_or_404(news_id)
    if request.method == 'POST':
        news.title = request.form.get('title')
        news.image = request.form.get('image')
        news.description = request.form.get('description')
        news.content = request.form.get('content')
        db.session.commit()
        flash('Новость обновлена.')
        return redirect(url_for('main.news_detail', news_id=news.id))
    return render_template('edit_news.html', news=news)


@main.route('/book/<book_id>', methods=['GET', 'POST'])
def book_detail(book_id):
    response = requests.get(f'https://www.googleapis.com/books/v1/volumes/{book_id}')
    book = response.json() if response.status_code == 200 else None
    message = None

    if request.method == 'POST':
        if current_user.is_authenticated:
            user_library = UserLibrary(user_id=current_user.id, book_id=book_id, title=book['volumeInfo']['title'],
                                       authors=book['volumeInfo'].get('authors', []))
            db.session.add(user_library)
            db.session.commit()
            message = "Книга добавлена в библиотеку."
        else:
            message = "Сначала нужно авторизоваться."

    return render_template('book_detail.html', book=book, message=message)


@main.route('/add_to_library/<book_id>', methods=['POST'])
@login_required
def add_to_library(book_id):
    response = requests.get(f'https://www.googleapis.com/books/v1/volumes/{book_id}')
    book = response.json() if response.status_code == 200 else None

    if book:
        user_library = UserLibrary(user_id=current_user.id, book_id=book_id, title=book['volumeInfo']['title'],
                                   authors=', '.join(book['volumeInfo'].get('authors', [])))
        db.session.add(user_library)
        db.session.commit()
        flash("Книга добавлена в библиотеку.")
    else:
        flash("Не удалось добавить книгу в библиотеку.")

    return redirect(url_for('main.book_detail', book_id=book_id))


@main.route('/user/<name>')
def hello_user(name):
    return render_template('user.html', name=name, current_user=current_user)


@main.route('/admin')
@login_required
@admin_required
def for_admin():
    return "For admin"


@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE)
def for_moderator():
    return "For moderator"


@main.route('/secret')
@login_required
def secret():
    return "Only for auth"


@main.route("/testConfirm")
def testConfirm():
    user = User.query.filter_by().first()
    tmp = user.generate_confirmation_token()
    user.confirm(tmp)


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user)


@main.route('/profile')
def profile():
    return render_template('profile.html')

