from fastapi import Header
from starlette.requests import Request
from starlette.responses import JSONResponse
from fastapi_models import ConnectionParams, SetDeviceDataParams
import pyzkaccess
import uvicorn
from fastapi import FastAPI

from typing import Dict, List

from fastapi import FastAPI
from pyzkaccess import ZKAccess, ZK100
from pyzkaccess.data import TableName, User


# TODO: see if there's a better way for this, maybe using an in-memory database?
# Though we might not need to as this app doesn't need to be scalable

# This is a dict key is the connection handle and value is a ZKAccess connected object
connected_devices: Dict[int, ZKAccess] = dict()


class DeviceNotConnectedException(Exception):
    def __init__(self, handle) -> None:
        self.handle = handle


def get_connected_device(handle: int) -> ZKAccess:
    try:
        return connected_devices[handle]
    except KeyError:
        raise DeviceNotConnectedException(handle)


app = FastAPI()


@app.exception_handler(DeviceNotConnectedException)
async def no_connected_device_exception_handler(request: Request, exc: DeviceNotConnectedException):
    return JSONResponse(
        status_code=400,
        content={"message": f"No connected device found with the handle: {exc.handle}; maybe try /connect first?"},
    )


@app.exception_handler(pyzkaccess.exceptions.ZKSDKError)
async def zksdkerror_handler(request: Request, exc: pyzkaccess.exceptions.ZKSDKError):
    return JSONResponse(
        status_code=400,
        content={
            "status": "error",
            "message": f"SDKError: {exc.msg}",
        },
    )


@app.get("/")
async def root():
    return {"message": "No Hello World"}


@app.post("/connect")
def connect(connection_parameters: ConnectionParams):
    print(connection_parameters)
    connstr = str(connection_parameters)

    try:
        zk = ZKAccess(connstr=connstr, device_model=ZK100)
        if not zk.handle:
            raise Exception("Unexpected error: handle not valid")

        connected_devices[zk.handle] = zk
    except pyzkaccess.exceptions.ZKSDKError as e:
        return {
            "status": "error",
            "message": str(e),
        }

    return {"status": "success", "handle": zk.handle}


# TODO: research if there is a better way than specifying handle: int = Header(...) in every single request
# TODO: research if there is a better way than specifying handle: int = Header(...) in every single request
# TODO: research if there is a better way than specifying handle: int = Header(...) in every single request
@app.post("/restart_device")
def restart_device(handle: int = Header(...)):
    response = get_connected_device(handle).restart()
    return {"status": "success", "response": response}


@app.post("/test_relay_unlock")
def test_relay_unlock(handle: int = Header(...)):
    response = get_connected_device(handle).relays.lock.switch_on(5)
    return {"status": "success", "response": response}


@app.get("/device_data")
def get_device_data(tablename: TableName, handle: int = Header(...)):
    data = get_connected_device(handle).get_data(tablename)
    return data


@app.post("/device_data")
def set_device_data(params: SetDeviceDataParams, handle: int = Header(...)):
    get_connected_device(handle).set_data(params.tablename, params.data)


@app.get("/users", response_model=List[User])
def get_all_users(handle: int = Header(...)):
    all_users = get_connected_device(handle).get_users()
    return all_users


@app.post("/users")
def add_user(users: List[User], handle: int = Header(...)):  # TODO: see if there's a better way to only specify handle param once for the whole app
    get_connected_device(handle).add_users(users)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
