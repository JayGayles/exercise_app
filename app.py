from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow_sqlalchemy import SQLAlchemySchema
from marshmallow import Schema, fields
from flask_migrate import Migrate
from dotenv import load_dotenv
import os
import random

app = Flask(__name__)


# database connector
load_dotenv('.env')

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Init db
db = SQLAlchemy(app)
migrate = Migrate(app, db)
# Init ma
ma = Marshmallow(app)

#Exercise Class/Model


class Exercise(db.Model):

    __tablename__ = 'exercise'
    id = db.Column(db.Integer, primary_key=True)
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

    def __repr__(self):
        return '<Exercise %d>' % self.id


db.create_all()

# Exercise Schema


class ExerciseSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'primary', 'secondary', 'function', 'mechanics', 'equipment', 'directions')


# Init Schema
exercise_schema = ExerciseSchema()

# Routes

@app.route('/')
def hello_world():
    return "Hello, World!"


# Endpoint to retrieve all exercises

@app.route('/exercises', methods=['GET'])
def index():
    get_exercises = Exercise.query.all()
    exercise_schema = ExerciseSchema(many=True)
    exercise = exercise_schema.dump(get_exercises)
    print(type(get_exercises))
    return make_response(jsonify({"exercises": exercise}))

# Endpoint to retrieve single exercise


@app.route('/exercises/<id>', methods=['GET'])
def get_exercise_by_id(id):
    exercise = Exercise.query.get(id)
    return exercise_schema.jsonify(exercise)

# Endpoint to add new exercise


@app.route('/exercises', methods=['POST'])
def add_exercise():
    name = request.json['name']
    primary = request.json['primary']
    secondary = request.json['secondary']
    function = request.json['function']
    mechanics = request.json['mechanics']
    equipment = request.json['equipment']
    directions = request.json['directions']
    new_exercise = Exercise(name, primary, secondary, function, mechanics, equipment, directions)

    db.session.add(new_exercise)
    db.session.commit()

    return exercise_schema.jsonify(new_exercise)

# Endpoint to update exercise


@app.route('/exercises/<id>', methods=['PUT'])
def update_exercise(id):
    exercise = Exercise.query.get(id)
    name = request.json['name']
    primary = request.json['primary']
    secondary = request.json['secondary']
    function = request.json['function']
    mechanics = request.json['mechanics']
    equipment = request.json['equipment']
    directions = request.json['directions']

    exercise.name = name
    exercise.primary = primary
    exercise.secondary = secondary
    exercise.function = function
    exercise.mechanics = mechanics
    exercise.equipment = equipment
    exercise.directions = directions
    db.session.commit()

    return exercise_schema.jsonify(exercise)

# Endpoint for deleting a record


@app.route("/exercises/<id>", methods=["DELETE"])
def delete_exercise(id):
    exercise = Exercise.query.get(id)
    db.session.delete(exercise)
    db.session.commit()

    return "Exercise was successfully deleted"

# Route to display all leg exercises


@app.route('/legs', methods=['GET'])
def legs():
    get_legs = Exercise.query.filter(Exercise.primary.ilike('Legs')).order_by(Exercise.id).all()
    exercise_schema = ExerciseSchema(many=True)
    exercise = exercise_schema.dump(get_legs)
    return make_response(jsonify({"leg_exercises": exercise}))


# Route to display all chest exercises
@app.route('/chest', methods=['GET'])
def chest():
    get_chest = Exercise.query.filter_by(primary='Chest').order_by(Exercise.id).all()
    exercise_schema = ExerciseSchema(many=True)
    exercise = exercise_schema.dump(get_chest)
    return make_response(jsonify({"chest_exercises": exercise}))


# Route to display exercises with primary muscle group as Chest or Legs
@app.route('/chestlegs', methods=['GET'])
def chestleg():
    get_chestleg = Exercise.query.filter(
        (Exercise.primary.ilike('Chest')) |
        (Exercise.primary.ilike('Legs'))
    ).order_by(Exercise.id).all()
    exercise_schema = ExerciseSchema(many=True)
    exercises = exercise_schema.dump(get_chestleg)
    return make_response(jsonify({"chest_and_leg_exercises": exercises}))


# Route to generate a workout based on muscle groups
@app.route('/generateworkout', methods=['POST'])
def generateworkout():
    data = request.json  # Get the request data
    muscle_groups = data.get('muscle_groups')  # Extract the muscle groups from the request

    if not muscle_groups:  # Check if muscle_groups is provided
        return jsonify({'error': 'Please provide muscle_groups'}), 400

    workout_plan = {}  # Initialize an empty workout plan
    for muscle in muscle_groups:
        # Query exercises where primary or secondary matches the muscle group
        exercises = Exercise.query.filter(
            (Exercise.primary.ilike(muscle)) |
            (Exercise.secondary.ilike(f"%{muscle}%"))
        ).all()

        if not exercises:  # If no exercises are found for the muscle group
            workout_plan[muscle] = []  # Add an empty list for that group
            continue

        # Randomly select up to 3 exercises
        selected_exercises = random.sample(exercises, min(3, len(exercises)))
        workout_plan[muscle] = [
            {"name": ex.name, "directions": ex.directions} for ex in selected_exercises
        ]

    # Return the generated workout plan as a JSON response
    return jsonify({'workout_plan': workout_plan})

if __name__ == "__main__":
    app.run(debug=True)