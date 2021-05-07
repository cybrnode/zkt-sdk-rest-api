from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_read_main():
    response = client.get("/")
    print(response.json())
    assert response.status_code == 200
    assert response.json() == {"message": "No Hello World"}
