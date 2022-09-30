from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField, SubmitField, FloatField, TextAreaField
from wtforms.validators import DataRequired

class RegisterForm(FlaskForm):
    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign Me Up")

class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

# class RubricCriterionForm(FlaskForm):
#     criterion = StringField("Criterion", validators=[DataRequired()])
#     description = TextAreaField("Description", validators=[DataRequired()])
#     weight = FloatField("Weight", validators=[DataRequired()])
#     submit = SubmitField("Add Criterion")

# class RubricForm(FlaskForm):
#     rubric_name = StringField("Rubric Name", validators=[DataRequired()])
#     submit = SubmitField("Create Rubric")