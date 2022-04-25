# Route to display all leg exercises
@app.route('/legs', methods=['GET'])
def legs():
    get_legs = Exercise.query.filter_by(primary='legs').order_by(Exercise.id).all()
    exercise_schema = ExerciseSchema(many=True)
    exercise = exercise_schema.dump(get_legs)
    return make_response(jsonify({"leg exercises": exercise}))


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

