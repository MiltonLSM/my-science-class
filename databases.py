from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from sqlalchemy.orm import relationship
from flask_login import UserMixin

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///science_class.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "welcome2THEcomewel"
Bootstrap(app)
db = SQLAlchemy(app)

#------------------------------------- DATA BASES ----------------------------------#

class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(250), nullable=False)
    last_name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), nullable=False)
    password = db.Column(db.String(250), nullable=False)
    group = db.Column(db.String(15), nullable=False)

class Rubric(db.Model):
    __tablename__ = "rubrics"
    id = db.Column(db.Integer, primary_key=True)
    rubric_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    items = relationship("RubricItem", back_populates="rubric") # (ONE) one rubric - many items
    activity = relationship("Activity", back_populates="rubric")

class RubricItem(db.Model):
    __tablename__ = "rubric_items"
    id = db.Column(db.Integer, primary_key=True)
    criterion = db.Column(db.String(250), nullable=False)
    description = db.Column(db.String(1000), nullable=False)
    weight = db.Column(db.Float(), nullable=False)
    rubric_id = db.Column(db.Integer, db.ForeignKey("rubrics.id")) # (MANY) The many have the foreingkey
    rubric = relationship("Rubric", back_populates="items") 

class Goal(db.Model):
    __tablename__ = "goals"
    code = db.Column(db.String(15), primary_key=True)
    goal_description = db.Column(db.String(1000), nullable=False)
    level = db.Column(db.String(250), nullable=False)
    competency = db.Column(db.String(250), nullable=False)
    topic = db.Column(db.String(250), nullable=False)
    activity = relationship("Activity", back_populates="goal")

class Activity(db.Model):
    __tablename__ = "activities"
    id = db.Column(db.Integer, primary_key=True)
    activity_name = db.Column(db.String(100), nullable=False)
    rubric_id = db.Column(db.Integer, db.ForeignKey("rubrics.id"))
    rubric = relationship("Rubric", back_populates="activity")
    goal_id = db.Column(db.String(15), db.ForeignKey("goals.code"))
    goal = relationship("Goal", back_populates="activity")