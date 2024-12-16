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
