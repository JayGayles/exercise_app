from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow_sqlalchemy import SQLAlchemySchema
from marshmallow import Schema, fields
from dotenv import load_dotenv
import os


app = Flask(__name__)


# database connector
load_dotenv('.env')

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")

# Init db
db = SQLAlchemy(app)

# Init ma
ma = Marshmallow(app)

#Exercise Class/Model

class Exercise(db.Model):

    __tablename__ = 'exercises'
    index = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    primary = db.Column(db.String(50))
    secondary = db.Column(db.String(50))
    function = db.Column(db.String(50))
    mechanics = db.Column(db.String(50))
    equipment = db.Column(db.String(50))
    directions = db.Column(db.String(3000))

    def __init__(self, name, primary, secondary, function, mechanics, equipment, directions):
        self.name = name
        self.primary = primary
        self.secondary = secondary
        self.function = function
        self.mechanics = mechanics
        self.equipment = equipment
        self.directions = directions

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

    def __repr__(self):
        return '<Exercise %d>' % self.index


db.create_all()

# Exercise Schema


class ExerciseSchema(ma.Schema):
    class Meta:
        fields = ('index', 'name', 'primary', 'secondary', 'function', 'mechanics', 'equipment', 'directions')


# Init Schema
exercise_schema = ExerciseSchema()

# Routes

@app.route('/')
def hello_world():
    return "Hello, World!"


# Route to display all exercises

@app.route('/exercises', methods=['GET'])
def index():
    get_exercises = Exercise.query.all()
    exercise_schema = ExerciseSchema(many=True)
    exercise = exercise_schema.dump(get_exercises)
    print(type(get_exercises))
    return make_response(jsonify({"exercises": exercise}))

# POST API to add new exercise


@app.route('/exercises', methods=['POST'])
def add_exercise():
    name = request.json('name')
    primary = request.json('primary')
    secondary = request.json('secondary')
    function = request.json('function')
    mechanics = request.json('mechanics')
    equipment = request.json('equipment')
    directions = request.json('directions')

    new_exercise = Exercise(name, primary, secondary, function, mechanics, equipment, directions)
    db.session.add(new_exercise)
    db.session.commit()

    return exercise_schema.jsonify(new_exercise)


if __name__ == "__main__":
    app.run(debug=True)