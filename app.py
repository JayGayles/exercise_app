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

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

    def __repr__(self):
        return '<Exercise %d>' % self.index


db.create_all()


class ExerciseSchema(SQLAlchemySchema):
    class Meta(SQLAlchemySchema.Meta):
        model = Exercise
        sqla_session = db.session

    index = fields.Number(dump_only=True)
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
    print(type(get_exercises))
    return make_response(jsonify({"exercises": exercise}))

# POST API to add new exercise
@app.route('/exercises', methods=['POST'])
def create_exercise():
    data = request.get_json()
    print(data)
    exercise = Exercise(data['name'],
                        data['primary'],
                        data['secondary'],
                        data['function'],
                        data['mechanics'],
                        data['equipment'],
                        data['directions'])
    db.session.add(exercise)
    db.session.commit()

    response = jsonify(exercise)
    return make_response(jsonify({"exercises": exercise}), 201)


if __name__ == "__main__":
    app.run(debug=True)