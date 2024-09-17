from marshmallow_sqlalchemy import SQLAlchemySchema
from marshmallow import fields
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Exercise Model


class Exercise(db.Model):
    __tablename__ = 'exercise'
    id = db.Column(db.Integer, primary_key=True)
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