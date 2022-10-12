from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField, SubmitField, FloatField, TextAreaField, SelectField
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

class RubricItemForm(FlaskForm):
    criterion = StringField("Criterion", validators=[DataRequired()])
    item_description = TextAreaField("Description")
    weight = FloatField("Weight", validators=[DataRequired()])
    submit = SubmitField("Add Item")
    edit = SubmitField("Edit Item")
    cancel = SubmitField("Cancel", render_kw={'formnovalidate':True})


class RubricForm(FlaskForm):
    rubric_name = StringField("Rubric Name", validators=[DataRequired()])
    rubric_description = TextAreaField("Description")
    # rubric_item = FieldList(FormField(RubricItemForm), min_entries=2)
    submit = SubmitField("Create Rubric")

class GoalForm(FlaskForm):
    code = StringField("CODE", validators=[DataRequired()])
    goal_description = TextAreaField("GOAL", validators=[DataRequired()])
    level = SelectField("LEVEL", choices=["Low", "Basic", "High", "Outstanding"], validators=[DataRequired()])
    competency = SelectField("COMPETENCY", choices=["Use of Scienctific Knowlege", "Inquiry", "Phenomena Explanation"])
    topic = StringField("CORE IDEA", validators=[DataRequired()])
    submit = SubmitField("ADD GOAL")
    edit = SubmitField("EDIT GOAL")