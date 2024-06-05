from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin
from app import db
from .models import User, Role, Book, UserLibrary, News

admin = Admin(name='Admin Panel')

admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Role, db.session))
admin.add_view(ModelView(Book, db.session))
admin.add_view(ModelView(UserLibrary, db.session))
admin.add_view(ModelView(News, db.session))
