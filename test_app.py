import pytest
from app import app, db
from models import Exercise

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.session.remove()
            db.drop_all()

def test_hello_world(client):
    response = client.get('/')
    assert response.status_code == 200
    assert response.data == b"Hello, World!"


def test_get_all_exercises(client):
    # Add mock data
    exercise = Exercise(name="Squat", primary="Legs", secondary="Glutes", function="Strength",
                        mechanics="Compound", equipment="Barbell", directions="Perform a squat.")
    db.session.add(exercise)
    db.session.commit()

    # Test the endpoint
    response = client.get('/exercises')
    data = response.get_json()
    assert response.status_code == 200
    assert "exercises" in data
    assert len(data["exercises"]) == 1
    assert data["exercises"][0]["name"] == "Squat"


def test_add_exercise(client):
    payload = {
        "name": "Bench Press",
        "primary": "Chest",
        "secondary": "Triceps",
        "function": "Strength",
        "mechanics": "Compound",
        "equipment": "Barbell",
        "directions": "Lie on a bench and press the bar up."
    }
    response = client.post('/exercises', json=payload)
    data = response.get_json()
    assert response.status_code == 200
    assert data["name"] == "Bench Press"

    # Verify it was added to the database
    exercises = Exercise.query.all()
    assert len(exercises) == 1
    assert exercises[0].name == "Bench Press"


def test_generate_workout(client):
    # Add mock data
    db.session.add(Exercise(name="Squat", primary="Legs", secondary="Glutes", function="Strength",
                            mechanics="Compound", equipment="Barbell", directions="Perform a squat."))
    db.session.add(Exercise(name="Deadlift", primary="Legs", secondary="Back", function="Strength",
                            mechanics="Compound", equipment="Barbell", directions="Perform a deadlift."))
    db.session.commit()

    # Test the endpoint
    payload = {"muscle_groups": ["Legs"]}
    response = client.post('/generateworkout', json=payload)
    data = response.get_json()
    assert response.status_code == 200
    assert "workout_plan" in data
    assert "Legs" in data["workout_plan"]
    assert len(data["workout_plan"]["Legs"]) > 0


def test_delete_exercise(client):
    # Add mock data
    exercise = Exercise(name="Squat", primary="Legs", secondary="Glutes", function="Strength",
                        mechanics="Compound", equipment="Barbell", directions="Perform a squat.")
    db.session.add(exercise)
    db.session.commit()

    # Delete the exercise
    response = client.delete(f'/exercises/{exercise.id}')
    assert response.status_code == 200

    # Verify it was removed from the database
    exercises = Exercise.query.all()
    assert len(exercises) == 0

# Fixture to set up the testing client and database
@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.session.remove()
            db.drop_all()

# Test root endpoint
def test_hello_world(client):
    response = client.get('/')
    assert response.status_code == 200
    assert response.data == b"Hello, World!"

# Test case-insensitive input handling for /generateworkout
def test_generate_workout_case_insensitive(client):
    db.session.add(Exercise(name="Squat", primary="Legs", secondary="Glutes", function="Strength",
                            mechanics="Compound", equipment="Barbell", directions="Perform a squat."))
    db.session.commit()

    response = client.post('/generateworkout', json={"muscle_groups": ["legs"]})
    assert response.status_code == 200
    data = response.get_json()
    assert "Legs" in data["workout_plan"]

    response = client.post('/generateworkout', json={"muscle_groups": ["LEGS"]})
    assert response.status_code == 200
    data = response.get_json()
    assert "Legs" in data["workout_plan"]

    response = client.post('/generateworkout', json={"muscle_groups": ["LeGs"]})
    assert response.status_code == 200
    data = response.get_json()
    assert "Legs" in data["workout_plan"]

# Test punctuation handling for /generateworkout
def test_generate_workout_punctuation(client):
    db.session.add(Exercise(name="Squat", primary="Legs", secondary="Glutes", function="Strength",
                            mechanics="Compound", equipment="Barbell", directions="Perform a squat."))
    db.session.add(Exercise(name="Bench Press", primary="Chest", secondary="Triceps", function="Strength",
                            mechanics="Compound", equipment="Barbell", directions="Press the barbell up."))
    db.session.commit()

    response = client.post('/generateworkout', json={"muscle_groups": ["legs!"]})
    assert response.status_code == 200
    data = response.get_json()
    assert "Legs" in data["workout_plan"]

    response = client.post('/generateworkout', json={"muscle_groups": ["chest, legs"]})
    assert response.status_code == 200
    data = response.get_json()
    assert "Chest" in data["workout_plan"]
    assert "Legs" in data["workout_plan"]

# Test input with spaces for /generateworkout
def test_generate_workout_spaces(client):
    db.session.add(Exercise(name="Squat", primary="Legs", secondary="Glutes", function="Strength",
                            mechanics="Compound", equipment="Barbell", directions="Perform a squat."))
    db.session.commit()

    response = client.post('/generateworkout', json={"muscle_groups": ["  legs  "]})
    assert response.status_code == 200
    data = response.get_json()
    assert "Legs" in data["workout_plan"]

# Test special characters in input for /generateworkout
def test_generate_workout_special_characters(client):
    db.session.add(Exercise(name="Squat", primary="Legs", secondary="Glutes", function="Strength",
                            mechanics="Compound", equipment="Barbell", directions="Perform a squat."))
    db.session.commit()

    response = client.post('/generateworkout', json={"muscle_groups": ["le!gs"]})
    assert response.status_code == 200
    data = response.get_json()
    assert "Legs" in data["workout_plan"]

# Test combined inputs for /generateworkout
def test_generate_workout_combined_inputs(client):
    db.session.add(Exercise(name="Squat", primary="Legs", secondary="Glutes", function="Strength",
                            mechanics="Compound", equipment="Barbell", directions="Perform a squat."))
    db.session.commit()

    response = client.post('/generateworkout', json={"muscle_groups": [" L*e@g,s! "]})
    assert response.status_code == 200
    data = response.get_json()
    assert "Legs" in data["workout_plan"]

# Test no matching exercises for given input
def test_generate_workout_no_matching_exercises(client):
    db.session.add(Exercise(name="Squat", primary="Legs", secondary="Glutes", function="Strength",
                            mechanics="Compound", equipment="Barbell", directions="Perform a squat."))
    db.session.commit()

    response = client.post('/generateworkout', json={"muscle_groups": ["arms"]})
    assert response.status_code == 200
    data = response.get_json()
    assert "Arms" in data["workout_plan"]
    assert len(data["workout_plan"]["Arms"]) == 0
