from app.main import app

def test_read_health(client):
    # Test health check route
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
