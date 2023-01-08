from flask import Flask, render_template, redirect, url_for, flash, abort, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_bootstrap import Bootstrap
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, UserMixin, LoginManager, login_required, current_user
from forms import ActivityForm, LoginForm, RegisterForm, RubricForm, RubricItemForm, GoalForm, GradeStudentForm
from databases import app, db, User, Rubric, RubricItem, Goal, Activity, ItemGrade, ActivityGrade



#------------------------------------ LOGIN MANAGER --------------------------------#

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#---------------------------------- CREATE DATABASES -------------------------------#

db.create_all()

#------------------------------------- URL ROUTES ----------------------------------#

def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.group != "ADMIN":
            return abort(403)
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def home():
    return render_template('index.html', current_user=current_user)


@app.route('/register', methods=["GET", "POST"])
def register():
    class_codes = {"CODE5A":"5A", "CODE5B":"5B", "CODE5C":"5C", "CODEADM":"ADMIN"}
    form = RegisterForm()
    if form.validate_on_submit(): 

        if User.query.filter_by(email=form.email.data).first():
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))

        hashed_and_salt_password = generate_password_hash(
            password=form.password.data, 
            method="pbkdf2:sha256",
            salt_length=8,
        )

        if form.class_code.data in class_codes:
            if class_codes[form.class_code.data] == form.group.data:
                new_user = User(
                    first_name = form.first_name.data,
                    last_name = form.last_name.data,
                    email = form.email.data,
                    password = hashed_and_salt_password,
                    group = form.group.data,
                )
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user)

                if form.group.data == "ADMIN":
                    return redirect(url_for("admin_home"))
                return redirect(url_for("student_home"))

            else:
                flash("Your class code does not match your group. Please enter a valid class code")
                return redirect(url_for('register'))
        
        else:
            flash("The class does not exist. Please enter a valid class code")
            return redirect(url_for('register'))

    return render_template('register.html', form=form, current_user=current_user)


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()

        if user == None:
            flash("The email doesn't exist. Please try again!")
            return redirect(url_for('login'))
        else:
            if check_password_hash(user.password, password):
                login_user(user)
                if user.group == "ADMIN":
                    return redirect(url_for('admin_home'))
                return redirect(url_for("student_home"))

            else:
                flash("Password incorrect. Please try again!")
                return redirect(url_for('login'))
        
    return render_template('login.html', form=form, current_user=current_user)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/admin-home')
@login_required
@admin_only
def admin_home():
    goals = Goal.query.all()
    activities = Activity.query.all()
    return render_template('admin-home.html', current_user=current_user, all_goals=goals, all_activities=activities)


@app.route("/new-rubric", methods=["GET", "POST"])
@login_required
@admin_only
def new_rubric():
    form = RubricForm()
    if form.validate_on_submit():
        new_rubric = Rubric(
            rubric_name = form.rubric_name.data,
            description = form.rubric_description.data
        )
        db.session.add(new_rubric)
        db.session.commit()
        return redirect(url_for("add_items", rubric_id=new_rubric.id))

    return render_template("new-rubric.html", form=form, current_user=current_user)


@app.route("/add-items/<int:rubric_id>", methods=["GET", "POST"])
@login_required
@admin_only
def add_items(rubric_id):
    form = RubricItemForm()
    requested_rubric = Rubric.query.get(rubric_id)

    if form.validate_on_submit():
        new_item = RubricItem(
            criterion = form.criterion.data,
            description = form.item_description.data,
            weight = form.weight.data,
            rubric = requested_rubric
        )
        
        
        db.session.add(new_item)
        db.session.commit()
        return redirect(url_for("add_items", rubric_id=requested_rubric.id))
    
    weight_sum = 0
    for item in requested_rubric.items:
        weight_sum += item.weight

    return render_template("add-items.html", rubric=requested_rubric, form=form, current_user=current_user, weight_sum=weight_sum)


@app.route("/edit-item/<int:item_id>", methods=["GET", "POST"])
@login_required
@admin_only
def edit_item(item_id):
    item = RubricItem.query.get(item_id) # Get the item from the database
    requested_rubric = Rubric.query.get(item.rubric_id)
    edit_form = RubricItemForm( #Create an instance for the rubric item
        criterion=item.criterion,
        item_description=item.description,
        weight=item.weight
    )
    if edit_form.validate_on_submit(): 
        if edit_form.cancel.data:
            return redirect(url_for("add_items", rubric_id=item.rubric_id))
        else:
            item.criterion = edit_form.criterion.data
            item.description = edit_form.item_description.data
            item.weight = edit_form.weight.data
            db.session.commit()
            return redirect(url_for("add_items", rubric_id=item.rubric_id))
    
    weight_sum = 0
    for item in requested_rubric.items:
        weight_sum += item.weight
    print(weight_sum)

    return render_template("add-items.html", rubric=requested_rubric, form=edit_form, is_editing=True, current_user=current_user, weight_sum=weight_sum)


@app.route("/delete-item/<int:item_id>")
@login_required
@admin_only
def delete_item(item_id):
    item_to_delete = RubricItem.query.get(item_id)
    db.session.delete(item_to_delete)
    db.session.commit()
    return redirect(url_for("add_items", rubric_id=item_to_delete.rubric_id))


@app.route("/add-goal", methods=["GET", "POST"])
@login_required
@admin_only
def add_goal():
    form = GoalForm()
    if form.validate_on_submit():

        if Goal.query.filter_by(code=form.code.data).first():
            flash("This code is already in use. Please change the code and try again.")
            return redirect(url_for('add_goal'))

        new_goal = Goal(
            code = form.code.data,
            goal_description = form.goal_description.data,
            level = form.level.data,
            competency = form.competency.data,
            topic = form.topic.data
        )
        db.session.add(new_goal)
        db.session.commit()
        return redirect(url_for("admin_home"))

    return render_template('goals.html', form=form, current_user=current_user)


@app.route("/edit-goal/<goal_code>", methods=["GET", "POST"])
@login_required
@admin_only
def edit_goal(goal_code):
    goal = Goal.query.get(goal_code)
    edit_form = GoalForm(
        code = goal.code,
        goal_description = goal.goal_description,
        level = goal.level,
        competency = goal.competency,
        topic = goal.topic
    )

    if edit_form.validate_on_submit():
        goal.code = edit_form.code.data
        goal.goal_description = edit_form.goal_description.data
        goal.level = edit_form.level.data
        goal.competency = edit_form.competency.data
        goal.topic = edit_form.topic.data
        db.session.commit()
        return redirect(url_for("admin_home"))

    return render_template("goals.html", form=edit_form, current_user=current_user, is_editing=True)


@app.route("/delete-goal/<goal_code>")
@login_required
@admin_only
def delete_goal(goal_code):
    goal_to_delete = Goal.query.get(goal_code)
    db.session.delete(goal_to_delete)
    db.session.commit()
    return redirect(url_for("admin_home"))


@app.route("/add-activity", methods=["GET", "POST"])
@login_required
@admin_only
def add_activity():
    form = ActivityForm()
    if form.validate_on_submit():
        new_activity = Activity(
            activity_name = form.activity_name.data,
            rubric = Rubric.query.get(form.rubric.data),
            goal = Goal.query.get(form.goal.data)
        )
        db.session.add(new_activity)
        db.session.commit()
        return redirect(url_for("admin_home"))

    return render_template('activity.html', current_user=current_user, form=form)


@app.route("/edit-act/<int:activity_id>", methods=["GET", "POST"])
@login_required
@admin_only
def edit_activity(activity_id):
    act = Activity.query.get(activity_id)
    edit_form = ActivityForm(
        activity_name = act.activity_name,
        rubric = act.rubric.id,
        goal = act.goal.code 
    )
    
    if edit_form.validate_on_submit():
        act.activity_name = edit_form.activity_name.data
        act.rubric = Rubric.query.get(edit_form.rubric.data)
        act.goal = Goal.query.get(edit_form.goal.data)
        db.session.commit()
        return redirect(url_for("admin_home"))

    return render_template("activity.html", current_user=current_user, form=edit_form)


@app.route("/delete-activity/<int:activity_id>")
@login_required
@admin_only
def delete_act(activity_id):
    act_to_delete = Activity.query.get(activity_id)
    db.session.delete(act_to_delete)
    db.session.commit()
    return redirect(url_for("admin_home"))


@app.route("/grade-activity/<int:activity_id>", methods=["GET", "POST"])
@login_required
@admin_only
def grade_activity(activity_id):
    activity = Activity.query.get(activity_id)
    users = User.query.all()
    form = GradeStudentForm()
    form.students.choices = [(user.id, user.last_name.upper() + " " + user.first_name.upper()) for user in User.query.filter_by(group='5A').all()]

    if request.method == 'POST':
        students = request.form.getlist('students')

        
        for student in students:
            item_points = 0

            for item in activity.rubric.items:
                points = (item.weight/100) * int(request.form.get(str(item.id)))
                item_points += points
                

                new_graded_item = ItemGrade(
                    items = item,
                    item_score = int(request.form.get(str(item.id))),
                    observation = request.form.get('obs'+str(item.id)),
                    user = User.query.filter_by(id=int(student)).first(),
                    activity = Activity.query.filter_by(id=(activity_id)).first()
                )
                db.session.add(new_graded_item)
            
            new_graded_activity = ActivityGrade(
                user = User.query.filter_by(id=int(student)).first(),
                activity = Activity.query.filter_by(id=(activity_id)).first(),
                activity_score = item_points
            )
            db.session.add(new_graded_activity)

        db.session.commit()
        return redirect(url_for("grade_activity", activity_id=activity.id))

    return render_template('grade-act.html', current_user=current_user, activity=activity, users=users, form=form)

@app.route("/grade-activity/<int:activity_id>/<group>")
def student(activity_id, group):
    students = User.query.filter_by(group=group).all()
    activity = Activity.query.get(activity_id)

    studentList = []

    for student in students:
        studentObj = {}
        studentObj['id'] = student.id
        studentObj['name'] = student.last_name.upper() + " " + student.first_name.upper()
        studentList.append(studentObj)

    return jsonify({'students':studentList})


@app.route("/report/<group>")
@login_required
@admin_only
def report_per_group(group):
    grades = ActivityGrade.query.all()
    students = User.query.filter_by(group=group).all()
    activities_data = Activity.query.all()
    activities = [activity for activity in activities_data]

    students_data_clean = []
    students_data = []
    grade_activity_list = [grade.activity for grade in grades]
    grade_user_list = [grade.user for grade in grades]
    grade_score_list = [grade.activity_score for grade in grades]

    for student in students:
        grades_per_student = []
        activities_per_student = []
        scores_per_student = []
        grades_per_student.append(student)
        for i in range(len(grade_user_list)):
           
            if student == grade_user_list[i]:
                
                activities_per_student.append(grade_activity_list[i])
                scores_per_student.append(grade_score_list[i])
        grades_per_student.append(activities_per_student)
        grades_per_student.append(scores_per_student)

        students_data.append(grades_per_student)  
    
   
    for score_data in students_data:
        organized_data = []
        organized_data.append(f"{score_data[0].last_name.upper()} {score_data[0].first_name.upper()}")
        for act in activities:
            if act in score_data[1]:
                organized_data.append(f"{score_data[2][score_data[1].index(act)]:.{2}f}")
            else:
                organized_data.append(" ")
        students_data_clean.append(tuple(organized_data))

    return render_template('report.html', current_user=current_user, grades=grades, data=students_data_clean, headers=activities)


@app.route("/report")
@login_required
@admin_only
def grades_report():
    activities_data = Activity.query.all()
    activities = [activity for activity in activities_data]
    return render_template('report.html', current_user=current_user, headers=activities)


@app.route('/grade-act')
@login_required
@admin_only
def grade_act():
    return render_template('grade.html', current_user=current_user)


@app.route("/student-home")
@login_required
def student_home():
    return render_template('student-home.html', current_user=current_user)


if __name__ == "__main__":
    app.run(debug=True)