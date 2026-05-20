"""
Test suite for Mergington High School Activities API
Uses AAA (Arrange-Act-Assert) pattern for test structure
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Provide a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to known state before each test"""
    # Store original state
    original = {k: {"participants": v["participants"][:]} for k, v in activities.items()}
    yield
    # Restore after test
    for activity_name, data in original.items():
        activities[activity_name]["participants"] = data["participants"]


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_all_activities_returns_200(self, client):
        """ARRANGE: N/A (no setup needed)
           ACT: Fetch all activities
           ASSERT: Response status is 200
        """
        # ACT
        response = client.get("/activities")

        # ASSERT
        assert response.status_code == 200

    def test_get_activities_returns_dict(self, client):
        """ARRANGE: N/A
           ACT: Fetch all activities
           ASSERT: Response is a dictionary
        """
        # ACT
        response = client.get("/activities")

        # ASSERT
        assert isinstance(response.json(), dict)

    def test_get_activities_contains_expected_activities(self, client):
        """ARRANGE: N/A (activities are predefined in app)
           ACT: Fetch all activities
           ASSERT: Response contains expected activity names
        """
        # ACT
        response = client.get("/activities")
        data = response.json()

        # ASSERT
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data

    def test_activity_has_required_fields(self, client):
        """ARRANGE: N/A
           ACT: Fetch activities
           ASSERT: Each activity has required fields
        """
        # ACT
        response = client.get("/activities")
        data = response.json()

        # ASSERT
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_new_participant_returns_200(self, client, reset_activities):
        """ARRANGE: New email for an activity
           ACT: Sign up the new participant
           ASSERT: Response status is 200 and success message is returned
        """
        # ARRANGE
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"

        # ACT
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # ASSERT
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]

    def test_signup_adds_participant_to_activity(self, client, reset_activities):
        """ARRANGE: An email and an activity
           ACT: Sign up the email for the activity
           ASSERT: Participant appears in activity's participants list
        """
        # ARRANGE
        activity_name = "Gym Class"
        email = "alice@mergington.edu"
        original_count = len(activities[activity_name]["participants"])

        # ACT
        client.post(f"/activities/{activity_name}/signup", params={"email": email})

        # ASSERT
        assert email in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == original_count + 1

    def test_signup_duplicate_participant_returns_400(self, client, reset_activities):
        """ARRANGE: A participant already signed up for an activity
           ACT: Try to sign up the same participant again
           ASSERT: Response status is 400 and error message is returned
        """
        # ARRANGE
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up

        # ACT
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # ASSERT
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_for_nonexistent_activity_returns_404(self, client):
        """ARRANGE: A nonexistent activity name
           ACT: Try to sign up for that activity
           ASSERT: Response status is 404
        """
        # ARRANGE
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"

        # ACT
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # ASSERT
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_signup_returns_correct_message_format(self, client, reset_activities):
        """ARRANGE: Valid email and activity
           ACT: Sign up for activity
           ASSERT: Response message format is correct
        """
        # ARRANGE
        activity_name = "Art Club"
        email = "bob@mergington.edu"

        # ACT
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # ASSERT
        message = response.json()["message"]
        assert email in message
        assert activity_name in message


class TestRemoveParticipant:
    """Tests for DELETE /activities/{activity_name}/participants endpoint"""

    def test_remove_existing_participant_returns_200(self, client, reset_activities):
        """ARRANGE: An activity with a participant
           ACT: Remove that participant
           ASSERT: Response status is 200 and success message is returned
        """
        # ARRANGE
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Known participant

        # ACT
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )

        # ASSERT
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]

    def test_remove_participant_deletes_from_list(self, client, reset_activities):
        """ARRANGE: A participant in an activity
           ACT: Remove that participant
           ASSERT: Participant no longer in the activity's participants list
        """
        # ARRANGE
        activity_name = "Programming Class"
        email = "emma@mergington.edu"
        original_count = len(activities[activity_name]["participants"])

        # ACT
        client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )

        # ASSERT
        assert email not in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == original_count - 1

    def test_remove_nonexistent_participant_returns_404(self, client, reset_activities):
        """ARRANGE: An activity and email not in its participants
           ACT: Try to remove that email
           ASSERT: Response status is 404
        """
        # ARRANGE
        activity_name = "Gym Class"
        email = "nonexistent@mergington.edu"

        # ACT
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )

        # ASSERT
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_remove_from_nonexistent_activity_returns_404(self, client):
        """ARRANGE: A nonexistent activity name
           ACT: Try to remove a participant from it
           ASSERT: Response status is 404
        """
        # ARRANGE
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"

        # ACT
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )

        # ASSERT
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_remove_returns_correct_message_format(self, client, reset_activities):
        """ARRANGE: A valid participant in an activity
           ACT: Remove that participant
           ASSERT: Response message format is correct
        """
        # ARRANGE
        activity_name = "Swimming Club"
        email = "noah@mergington.edu"

        # ACT
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )

        # ASSERT
        message = response.json()["message"]
        assert email in message
        assert activity_name in message


class TestRootEndpoint:
    """Tests for GET / endpoint"""

    def test_root_redirects_to_static(self, client):
        """ARRANGE: N/A
           ACT: Request root endpoint with redirect following disabled
           ASSERT: Response status is 307 (redirect)
        """
        # ACT
        response = client.get("/", follow_redirects=False)

        # ASSERT
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
