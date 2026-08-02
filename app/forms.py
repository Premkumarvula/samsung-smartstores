"""
Form definitions using Flask-WTF.

Centralizing validation here (instead of ad-hoc checks in routes/templates)
keeps business rules in one place and gives us CSRF protection for free.
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, FloatField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo, NumberRange, Optional


class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField(
        "Password",
        validators=[DataRequired(), Length(min=8, message="Password must be at least 8 characters.")],
    )
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[DataRequired(), EqualTo("password", message="Passwords must match.")],
    )


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])


class ProductForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=100)])
    price = FloatField("Price", validators=[DataRequired(), NumberRange(min=0)])
    description = TextAreaField("Description", validators=[Optional(), Length(max=500)])
    image = StringField("Image filename", validators=[Optional(), Length(max=100)])
    stock = IntegerField("Stock", validators=[DataRequired(), NumberRange(min=0)])
