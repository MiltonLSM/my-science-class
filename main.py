from flask import Flask, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_bootstrap import Bootstrap
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, UserMixin, LoginManager, login_required, current_user
from forms import LoginForm, RegisterForm, RubricForm, RubricItemForm

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///science_class.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "welcome2THEcomewel"
Bootstrap(app)
db = SQLAlchemy(app)


#------------------------------------ LOGIN MANAGER --------------------------------#

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(admin_id):
    return Admin.query.get(int(admin_id))


#------------------------------------- DATA BASES ----------------------------------#

class Admin(db.Model, UserMixin):
    __tablename__ = "admin-users"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(250), nullable=False)
    last_name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), nullable=False)
    password = db.Column(db.String(250), nullable=False)

class Rubric(db.Model):
    __tablename__ = "rubrics"
    id = db.Column(db.Integer, primary_key=True)
    rubric_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    items = relationship("RubricItem", back_populates="rubric")

class RubricItem(db.Model):
    __tablename__ = "rubric_items"
    id = db.Column(db.Integer, primary_key=True)
    criterion = db.Column(db.String(250), nullable=False)
    description = db.Column(db.String(1000), nullable=False)
    weight = db.Column(db.Float(), nullable=False)
    rubric_id = db.Column(db.Integer, db.ForeignKey("rubrics.id"))
    rubric = relationship("Rubric", back_populates="items")

db.create_all()


#------------------------------------- URL ROUTES ----------------------------------#

@app.route('/')
def home():
    return render_template('index.html', current_user=current_user)

@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit(): 

        if Admin.query.filter_by(email=form.email.data).first():
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))

        hashed_and_salt_password = generate_password_hash(
            password=form.password.data, 
            method="pbkdf2:sha256",
            salt_length=8,
        )

        new_admin = Admin(
            first_name = form.first_name.data,
            last_name = form.last_name.data,
            email = form.email.data,
            password = hashed_and_salt_password
        )

        db.session.add(new_admin)
        db.session.commit()
        login_user(new_admin)
        return redirect(url_for("admin_home"))

    return render_template('register.html', form=form, current_user=current_user)


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = Admin.query.filter_by(email=email).first()

        if user == None:
            flash("The email doesn't exist. Please try again!")
            return redirect(url_for('login'))
        else:
            if check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for('admin_home'))
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
def admin_home():
    return render_template('admin-home.html', current_user=current_user)


@app.route("/new-rubric", methods=["GET", "POST"])
@login_required
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
    print(weight_sum)

    return render_template("add-items.html", rubric=requested_rubric, form=form, current_user=current_user, weight_sum=weight_sum)


@app.route("/edit-item/<int:item_id>", methods=["GET", "POST"])
@login_required
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
def delete_item(item_id):
    item_to_delete = RubricItem.query.get(item_id)
    db.session.delete(item_to_delete)
    db.session.commit()
    return redirect(url_for("add_items", rubric_id=item_to_delete.rubric_id))


@app.route('/grade-act')
@login_required
def grade_act():
    return render_template('grade.html', current_user=current_user)


if __name__ == "__main__":
    app.run(debug=True)