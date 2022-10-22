from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField, SubmitField, FloatField, TextAreaField, SelectField, FormField
from wtforms.validators import DataRequired, Optional
from databases import Rubric, Goal


class RegisterForm(FlaskForm):
    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    group = SelectField("Group", choices=["Choose your group", "5A", "5B", "5C", "ADMIN"], validators=[Optional()])
    class_code = StringField("Class Code", validators=[DataRequired()])
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
    submit = SubmitField("Create Rubric")


class GoalForm(FlaskForm):
    code = StringField("CODE", validators=[DataRequired()])
    goal_description = TextAreaField("GOAL", validators=[DataRequired()])
    level = SelectField("LEVEL", choices=["Low", "Basic", "High", "Outstanding"], validators=[DataRequired()])
    competency = SelectField("COMPETENCY", choices=["Use of Scienctific Knowlege", "Inquiry", "Phenomena Explanation"])
    topic = StringField("CORE IDEA", validators=[DataRequired()])
    submit = SubmitField("ADD GOAL")
    edit = SubmitField("EDIT GOAL")


class ActivityForm(FlaskForm):
    activity_name = StringField("Activity", validators=[DataRequired()])
    rubric = SelectField("Rubric")
    goal = SelectField("Goal", validators=[DataRequired()])
    submit = SubmitField("Add Activity")

    def __init__(self, *args, **kwargs):
        super(ActivityForm, self).__init__(*args, **kwargs)
        self.goal.choices = [(goal.code) for goal in Goal.query.all()]
        self.rubric.choices = [(rubric.id, rubric.rubric_name) for rubric in Rubric.query.all()]