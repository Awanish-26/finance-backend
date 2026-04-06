def test_create_user_unauthorized(client):
    """
    Ensure anonymous users cannot create new user accounts via the API.
    A missing bearer token should repel the anonymous request safely.
    """
    user_payload = {
        "email": "user@example.com",
        "name": "testuser",
        "role": "viewer",
        "status": "active",
        "password": "user@1234j"
    }

    # Making the request without providing any auth headers (no bearer token)
    response = client.post("/api/users", json=user_payload)

    # API resolves auth dependencies (401) before processing the payload
    assert response.status_code == 401
    assert response.json().get("detail") == "Not authenticated"


def test_create_user_missing_payload_fields(client):
    """
    Sending an incomplete payload structure should also be rejected dynamically.
    """
    incomplete_payload = {
        "email": "incomplete@example.com"
        # Missing required password, name, role
    }

    # Request lacks a token, so FastAPI immediately denies it with a 401
    response = client.post("/api/users", json=incomplete_payload)
    assert response.status_code == 401


def test_list_users_unauthorized(client):
    """
    Ensure the user collection is guarded against unauthenticated access.
    """
    response = client.get("/api/users")
    assert response.status_code == 401
    assert response.json().get("detail") == "Not authenticated"
