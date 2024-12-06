from marshmallow_sqlalchemy import SQLAlchemySchema
from marshmallow import fields
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# Exercise Model


class Exercise(db.Model):
    __tablename__ = 'exercise'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    primary = db.Column(db.String(50), nullable=False)
    secondary = db.Column(db.String(50))
    function = db.Column(db.String(50))
    mechanics = db.Column(db.String(50))
    equipment = db.Column(db.String(50))
    directions = db.Column(db.String(3000), nullable=False)

    def __init__(self, name, primary, secondary, function, mechanics, equipment, directions):
        self.name = name
        self.primary = primary
        self.secondary = secondary
        self.function = function
        self.mechanics = mechanics
        self.equipment = equipment
        self.directions = directions

    def __repr__(self):
        return f'<Exercise {self.name}>'

# Exercise Schema using Marshmallow


class ExerciseSchema(SQLAlchemySchema):
    class Meta:
        model = Exercise
        sqla_session = db.session

    id = fields.Number(dump_only=True)
    name = fields.String(required=True)
    primary = fields.String(required=True)
    secondary = fields.String()
    function = fields.String()
    mechanics = fields.String()
    equipment = fields.String()
    directions = fields.String(required=True)


# WorkoutLog Model
class WorkoutLog(db.Model):
    __tablename__ = 'workout_log'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercise.id'), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    sets = db.Column(db.Integer, nullable=False)
    reps_per_set = db.Column(db.String, nullable=False)  # e.g., "12,10,8" for each set
    weight = db.Column(db.Float, nullable=False)
    notes = db.Column(db.String(300), nullable=True)

    def __init__(self, user_id, exercise_id, sets, reps_per_set, weight, notes=""):
        self.user_id = user_id
        self.exercise_id = exercise_id
        self.sets = sets
        self.reps_per_set = reps_per_set
        self.weight = weight
        self.notes = notes

    def __repr__(self):
        return f'<WorkoutLog for Exercise {self.exercise_id}>'

# WorkoutLog Schema using Marshmallow


class WorkoutLogSchema(SQLAlchemySchema):
    class Meta:
        model = WorkoutLog
        sqla_session = db.session

    id = fields.Number(dump_only=True)
    user_id = fields.Integer(required=True)
    exercise_id = fields.Integer(required=True)
    date = fields.DateTime(dump_only=True)
    sets = fields.Integer(required=True)
    reps_per_set = fields.String(required=True)
    weight = fields.Float(required=True)
    notes = fields.String()
