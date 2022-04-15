from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from marshmallow_sqlalchemy import SQLAlchemySchema
from marshmallow import fields
import os

app = Flask(__name__)

# Connector
db_name = "exercise_db"
connectString = os.getenv('db.connect')

db = SQLAlchemy(app)


# Model
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
        return '<Product %d>' % self.id


db.create_all()


class ExerciseSchema(SQLAlchemySchema):
    class Meta(SQLAlchemySchema.Meta):
        model = Exercise
        sqla_session = db.session

    id = fields.Number(dump_only=True)
    name = fields.String(required=True)
    primary = fields.String(required=True)
    secondary = fields.String(required=True)
    function = fields.String(required=True)
    mechanics = fields.String(required=True)
    equipment = fields.String(required=True)
    directions = fields.String(required=True)


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
    return make_response(jsonify({"exercises": exercise}))


# Route to display all leg exercises
@app.route('/legs', methods=['GET'])
def legs():
    get_legs = Exercise.query.filter_by(primary='legs').order_by(Exercise.id).all()
    exercise_schema = ExerciseSchema(many=True)
    exercise = exercise_schema.dump(get_legs)
    return make_response(jsonify({"exercises": exercise}))


# Route to display all chest exercises
@app.route('/chest', methods=['GET'])
def chest():
    get_chest = Exercise.query.filter_by(primary='chest').order_by(Exercise.id).all()
    exercise_schema = ExerciseSchema(many=True)
    exercise = exercise_schema.dump(get_chest)
    return make_response(jsonify({"exercises": exercise}))


# Route to display all chest/leg exercises
@app.route('/chestlegs', methods=['GET'])
def chestleg():
    get_chestleg = Exercise.query.filter(primary=('chest' | 'legs')).order_by(Exercise.id).all()
    exercise_schema = ExerciseSchema(many=True)
    exercise = exercise_schema.dump(get_chest)


if __name__ == "__main__":
    app.run(debug=True)
