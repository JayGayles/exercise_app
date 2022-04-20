from marshmallow_sqlalchemy import SQLAlchemySchema
from marshmallow import fields

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