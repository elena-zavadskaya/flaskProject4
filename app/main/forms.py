from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, EqualTo, Length


class UserForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired(),
                                                   EqualTo('confirm_password', message='Пароли должны совпадать')])
    confirm_password = PasswordField(
        'Повторите пароль', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])

    submit = SubmitField('Войти')


class NewsForm(FlaskForm):
    title = StringField('Название', validators=[
        DataRequired(), Length(max=128)])
    image = StringField('Изображение URL', validators=[Length(max=256)])
    description = TextAreaField('Описание', validators=[Length(max=256)])
    content = TextAreaField('Текст', validators=[DataRequired()])
    submit = SubmitField('Отправить')
