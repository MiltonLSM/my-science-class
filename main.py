from flask import Flask, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, UserMixin, LoginManager
from forms import LoginForm, RegisterForm

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

db.create_all()


#------------------------------------- URL ROUTES ----------------------------------#

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

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

    return render_template('register.html', form=form)

@app.route('/grade-act')
def grade_act():
    return render_template('grade.html')

@app.route('/admin-home')
def admin_home():
    return render_template('admin-home.html')

@app.route("/new-rubric")
def new_rubric():
    return render_template("new-rubric.html")

if __name__ == "__main__":
    app.run(debug=True)