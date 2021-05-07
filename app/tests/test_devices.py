from typing import List
from fastapi import websockets
from fastapi.testclient import TestClient

from app.main import app
from pyzkaccess.data import User

client = TestClient(app)


class TestIDKWHATTOCALLTHISCLASS:
    TEST_DEVICE_IP = "192.168.10.201"

    def setup(self):
        self.handle = self.connect(self.TEST_DEVICE_IP)

    def connect(self, ip):
        test_device_connstr = {"protocol": "TCP", "ip_address": ip, "port": 14370, "timeout": 4000, "passwd": ""}

        response = client.post("/devices/connect", json=test_device_connstr)
        assert response.status_code == 200
        assert response.json().get("status", "") == "success"
        assert response.json().get("handle", "") != ""

        return response.json()["handle"]

    def get_all_users(self) -> List[User]:
        response = client.get(f"/devices/{self.handle}/users")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

        users = list(map(lambda u: User(**u), response.json()))
        return users

    def test_get_users_should_have_200_status_code(self):
        self.get_all_users()

    def test_delete_user_by_pin_should_delete_user(self):
        users = self.get_all_users()
        for user in users:
            r = client.delete(f"/devices/{self.handle}/users/{user.Pin}").json()
            assert r.get("status") == "success"

        assert len(self.get_all_users()) == 0

    def test_get_doors_should___well___get_doors(self):
        response = client.get(f"/devices/{self.handle}/config/doors")

        print(response.text)
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    async def hello(self):
        print("HAAALOOO")
        uri = f"ws://localhost:8000/{self.handle}/realtimelogs"
        async with websockets.connect(uri) as websocket:
            await websocket.send("Hello world!")
            await websocket.recv()

    def test_hello(self):
        print("HAAALOOO")
        with client.websocket_connect(f"/devices/{self.handle}/realtimelogs") as websocket:
            expected_headers = {
                "accept": "*/*",
                "accept-encoding": "gzip, deflate",
                "connection": "upgrade",
                "host": "testserver",
                "user-agent": "testclient",
                "sec-websocket-key": "testserver==",
                "sec-websocket-version": "13",
            }
            while True:
                data = websocket.receive_json()
                print(data)
            assert data == {"headers": expected_headers}

    # def test_update_user_should_update_the_user(self):
    #     raise NotImplementedError()
