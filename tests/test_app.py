import os
import io
import pytest
from fastapi.testclient import TestClient
from main import app, STORAGE_DIR

client = TestClient(app)

@pytest.fixture(autouse=True)
def clean_storage():
    """Изтрива файловете в storage преди всеки тест."""
    for f in STORAGE_DIR.iterdir():
        if f.is_file():
            f.unlink()
    yield


def test_root_endpoint():
    """Тест за началния endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "File Storage API" in data["message"]
    assert "GET /files/{filename}" in data["endpoints"]


def test_health_check():
    """Тест за health check"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data


def test_store_file_and_get_file():
    """Тест за качване и изтегляне на файл"""
    test_content = b"hello world"
    response = client.post(
        "/files",
        files={"file": ("test.txt", io.BytesIO(test_content), "text/plain")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "File stored successfully"
    assert data["filename"] == "test.txt"

    get_response = client.get("/files/test.txt")
    assert get_response.status_code == 200
    assert get_response.content == test_content


def test_list_files():
    """Тест за списък с файлове"""
    for i in range(2):
        client.post(
            "/files",
            files={"file": (f"file_{i}.txt", io.BytesIO(b"data"), "text/plain")}
        )
    response = client.get("/files")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 2
    assert all(f.startswith("file_") for f in data["files"])


def test_metrics_endpoint():
    """Тест за метрики"""
    client.post(
        "/files",
        files={"file": ("file.txt", io.BytesIO(b"123"), "text/plain")}
    )
    response = client.get("/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "files_stored_total" in data
    assert "total_storage_bytes" in data
    assert data["files_current"] >= 1
