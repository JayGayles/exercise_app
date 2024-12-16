from flask import Blueprint, request, jsonify, make_response
from models import db, Exercise, ExerciseSchema
import random

routes = Blueprint('routes', __name__)

exercise_schema = ExerciseSchema()


@routes.route('/exercises', methods=['GET'])
def index():
    get_exercises = Exercise.query.all()
    exercise_schema = ExerciseSchema(many=True)
    exercises = exercise_schema.dump(get_exercises)
    return make_response(jsonify({"exercises": exercises}))


@routes.route('/exercises/<int:id>', methods=['GET'])
def get_exercise_by_id(id):
    exercise = Exercise.query.get(id)
    return exercise_schema.jsonify(exercise)


@routes.route('/exercises', methods=['POST'])
def add_exercise():
    data = request.json
    new_exercise = Exercise(
        name=data['name'],
        primary=data['primary'],
        secondary=data['secondary'],
        function=data['function'],
        mechanics=data['mechanics'],
        equipment=data['equipment'],
        directions=data['directions']
    )
    db.session.add(new_exercise)
    db.session.commit()
    return exercise_schema.jsonify(new_exercise)


@routes.route('/exercises/<int:id>', methods=['PUT'])
def update_exercise(id):
    exercise = Exercise.query.get(id)
    data = request.json
    exercise.name = data['name']
    exercise.primary = data['primary']
    exercise.secondary = data['secondary']
    exercise.function = data['function']
    exercise.mechanics = data['mechanics']
    exercise.equipment = data['equipment']
    exercise.directions = data['directions']
    db.session.commit()
    return exercise_schema.jsonify(exercise)


@routes.route('/exercises/<int:id>', methods=['DELETE'])
def delete_exercise(id):
    exercise = Exercise.query.get(id)
    db.session.delete(exercise)
    db.session.commit()
    return jsonify({"message": "Exercise was successfully deleted"})


@routes.route('/legs', methods=['GET'])
def legs():
    get_legs = Exercise.query.filter(Exercise.primary.ilike('Legs')).order_by(Exercise.id).all()
    exercise_schema = ExerciseSchema(many=True)
    exercises = exercise_schema.dump(get_legs)
    return make_response(jsonify({"leg_exercises": exercises}))


@routes.route('/chest', methods=['GET'])
def chest():
    get_chest = Exercise.query.filter_by(primary='Chest').order_by(Exercise.id).all()
    exercise_schema = ExerciseSchema(many=True)
    exercises = exercise_schema.dump(get_chest)
    return make_response(jsonify({"chest_exercises": exercises}))


@routes.route('/chestlegs', methods=['GET'])
def chestleg():
    get_chestleg = Exercise.query.filter(
        (Exercise.primary.ilike('Chest')) | (Exercise.primary.ilike('Legs'))
    ).order_by(Exercise.id).all()
    exercise_schema = ExerciseSchema(many=True)
    exercises = exercise_schema.dump(get_chestleg)
    return make_response(jsonify({"chest_and_leg_exercises": exercises}))


@routes.route('/generateworkout', methods=['POST'])
def generateworkout():
    data = request.json
    muscle_groups = data.get('muscle_groups')
    if not muscle_groups:
        return jsonify({'error': 'Please provide muscle_groups'}), 400

    workout_plan = {}
    for muscle in muscle_groups:
        exercises = Exercise.query.filter(
            (Exercise.primary.ilike(muscle)) | (Exercise.secondary.ilike(f"%{muscle}%"))
        ).all()
        if not exercises:
            workout_plan[muscle] = []
            continue

        selected_exercises = random.sample(exercises, min(3, len(exercises)))
        workout_plan[muscle] = [
            {"name": ex.name, "directions": ex.directions} for ex in selected_exercises
        ]

    return jsonify({'workout_plan': workout_plan})
