from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture
def client():
    original_activities = deepcopy(activities)
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        activities.clear()
        activities.update(original_activities)


def test_get_activities_returns_available_activities(client):
    # Arrange
    activity_name = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert activity_name in response.json()
    assert "participants" in response.json()[activity_name]


def test_signup_adds_participant(client):
    # Arrange
    activity_name = "Basketball Team"
    participant_email = "new.student@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": participant_email},
    )

    # Assert
    assert response.status_code == 200
    assert participant_email in client.get("/activities").json()[activity_name]["participants"]


def test_signup_rejects_duplicate_participant(client):
    # Arrange
    activity_name = "Chess Club"
    participant_email = activities[activity_name]["participants"][0]
    original_participant_count = len(activities[activity_name]["participants"])

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": participant_email},
    )

    # Assert
    assert response.status_code == 400
    assert len(activities[activity_name]["participants"]) == original_participant_count


def test_signup_returns_not_found_for_unknown_activity(client):
    # Arrange
    activity_name = "Unknown Activity"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": "student@mergington.edu"},
    )

    # Assert
    assert response.status_code == 404


def test_delete_unregisters_participant(client):
    # Arrange
    activity_name = "Basketball Team"
    participant_email = "student.to.remove@mergington.edu"
    activities[activity_name]["participants"].append(participant_email)

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": participant_email},
    )

    # Assert
    assert response.status_code == 200
    assert participant_email not in client.get("/activities").json()[activity_name]["participants"]


def test_delete_returns_not_found_for_unregistered_participant(client):
    # Arrange
    activity_name = "Basketball Team"
    participant_email = "not.registered@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": participant_email},
    )

    # Assert
    assert response.status_code == 404


def test_delete_returns_not_found_for_unknown_activity(client):
    # Arrange
    activity_name = "Unknown Activity"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": "student@mergington.edu"},
    )

    # Assert
    assert response.status_code == 404