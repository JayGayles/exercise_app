import pytest
from app import app, db
from models import Exercise

@pytest.fixture
def client():
    """Fixture to set up the testing client and database."""
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

# ---------- Basic Endpoint Tests ---------- #

def test_hello_world(client):
    """Test root endpoint."""
    response = client.get('/')
    assert response.status_code == 200
    assert response.data == b"Hello, World!"

# ---------- Exercise CRUD Tests ---------- #

def test_get_all_exercises(client):
    """Test retrieving all exercises."""
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
    """Test adding a new exercise."""
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

def test_delete_exercise(client):
    """Test deleting an exercise."""
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

# ---------- Workout Generation Tests ---------- #

def test_generate_workout(client):
    """Test generating a workout based on muscle groups."""
    db.session.add(Exercise(name="Squat", primary="Legs", secondary="Glutes", function="Strength",
                            mechanics="Compound", equipment="Barbell", directions="Perform a squat."))
    db.session.add(Exercise(name="Deadlift", primary="Legs", secondary="Back", function="Strength",
                            mechanics="Compound", equipment="Barbell", directions="Perform a deadlift."))
    db.session.commit()

    response = client.post('/generateworkout', json={"muscle_groups": ["Legs"]})
    data = response.get_json()
    assert response.status_code == 200
    assert "workout_plan" in data
    assert "legs" in data["workout_plan"]
    assert len(data["workout_plan"]["legs"]) > 0

# ---------- Input Formatting Tests for /generateworkout ---------- #

def test_generate_workout_case_insensitive(client):
    """Test case-insensitive input handling."""
    db.session.add(Exercise(name="Squat", primary="Legs", secondary="Glutes", function="Strength",
                            mechanics="Compound", equipment="Barbell", directions="Perform a squat."))
    db.session.commit()

    for test_input in ["legs", "LEGS", "LeGs"]:
        response = client.post('/generateworkout', json={"muscle_groups": [test_input]})
        assert response.status_code == 200
        data = response.get_json()
        assert "legs" in data["workout_plan"]

def test_generate_workout_punctuation(client):
    """Test handling punctuation in input."""
    db.session.add(Exercise(name="Squat", primary="Legs", secondary="Glutes", function="Strength",
                            mechanics="Compound", equipment="Barbell", directions="Perform a squat."))
    db.session.commit()

    response = client.post('/generateworkout', json={"muscle_groups": ["legs!"]})
    assert response.status_code == 200
    data = response.get_json()
    assert "legs" in data["workout_plan"]

def test_generate_workout_spaces(client):
    """Test handling spaces in input."""
    db.session.add(Exercise(name="Squat", primary="Legs", secondary="Glutes", function="Strength",
                            mechanics="Compound", equipment="Barbell", directions="Perform a squat."))
    db.session.commit()

    response = client.post('/generateworkout', json={"muscle_groups": ["  legs  "]})
    assert response.status_code == 200
    data = response.get_json()
    assert "legs" in data["workout_plan"]

def test_generate_workout_multiple_muscles(client):
    """Test handling multiple muscle groups in input."""
    db.session.add(Exercise(name="Squat", primary="Legs", secondary="Glutes", function="Strength",
                            mechanics="Compound", equipment="Barbell", directions="Perform a squat."))
    db.session.add(Exercise(name="Bench Press", primary="Chest", secondary="Triceps", function="Strength",
                            mechanics="Compound", equipment="Barbell", directions="Press the barbell up."))
    db.session.commit()

    response = client.post('/generateworkout', json={"muscle_groups": ["legs", "chest"]})
    data = response.get_json()
    assert response.status_code == 200
    assert "legs" in data["workout_plan"]
    assert "chest" in data["workout_plan"]

def test_generate_workout_unknown_muscle(client):
    """Test unknown muscle group (should return empty list)."""
    response = client.post('/generateworkout', json={"muscle_groups": ["arms"]})
    data = response.get_json()
    assert response.status_code == 200
    assert "arms" in data["workout_plan"]
    assert len(data["workout_plan"]["arms"]) == 0

def test_generate_workout_invalid_input(client):
    """Test invalid inputs for /generateworkout."""
    invalid_inputs = [
        {"muscle_groups": []},  # Empty array
        {},  # Missing key
        {"muscle_groups": [123]},  # Numeric input
        {"muscle_groups": [None]},  # None input
        {"muscle_groups": "legs"},  # String instead of list
        {"muscle_groups": ["l" * 500]}  # Overly long string
    ]

    for payload in invalid_inputs:
        response = client.post('/generateworkout', json=payload)
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data