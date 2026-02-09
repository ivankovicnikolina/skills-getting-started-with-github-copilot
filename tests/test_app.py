from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)
BASELINE_ACTIVITIES = deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    activities.clear()
    activities.update(deepcopy(BASELINE_ACTIVITIES))
    yield


def test_get_activities_returns_data():
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_adds_participant():
    activity_name = "Chess Club"
    email = "new-student@mergington.edu"

    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    assert response.status_code == 200
    data = response.json()
    assert email in activities[activity_name]["participants"]
    assert "Signed up" in data["message"]


def test_signup_duplicate_participant_rejected():
    activity_name = "Soccer Club"
    email = "liam@mergington.edu"

    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Student already signed up for this activity"


def test_unregister_removes_participant():
    activity_name = "Programming Class"
    email = "emma@mergington.edu"

    response = client.post(
        f"/activities/{activity_name}/unregister",
        params={"email": email},
    )

    assert response.status_code == 200
    data = response.json()
    assert email not in activities[activity_name]["participants"]
    assert "Unregistered" in data["message"]


def test_unregister_missing_participant_returns_404():
    activity_name = "Math Olympiad"
    email = "missing@mergington.edu"

    response = client.post(
        f"/activities/{activity_name}/unregister",
        params={"email": email},
    )

    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Student not registered for this activity"
