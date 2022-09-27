from flask import Flask, render_template
from flask_bootstrap import Bootstrap

app = Flask(__name__)
Bootstrap(app)

#------------------------------------- URL ROUTES ----------------------------------#

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

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