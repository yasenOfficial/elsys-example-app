from locust import HttpUser, task, between

class FileStorageUser(HttpUser):
    wait_time = between(1, 3)

    @task(2)
    def ping_health(self):
        """Тест за /health endpoint"""
        self.client.get("/health")

    @task(1)
    def list_files(self):
        """Тест за /files endpoint"""
        self.client.get("/files")

    @task(1)
    def upload_file(self):
        """Тест за POST /files"""
        files = {"file": ("locust_test.txt", b"Load test data", "text/plain")}
        self.client.post("/files", files=files)
