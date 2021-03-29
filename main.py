from fastapi_models import ConnectionParams, SetDeviceDataParams
import pyzkaccess
import uvicorn
from fastapi import FastAPI

from typing import Dict, Optional

from fastapi import FastAPI
from pydantic import BaseModel
from pyzkaccess import ZKAccess, ZK100
from pyzkaccess.data import TableName


# TODO: see if there's a better way for this, maybe using an in-memory database?
# Though we might not need to as this app doesn't need to be scalable

# This is a dict key is the connection handle and value is a ZKAccess connected object
connected_devices: Dict[int, ZKAccess] = dict()


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "No Hello World"}


@app.post("/connect")
def connect(connection_parameters: ConnectionParams):
    print(connection_parameters)
    connstr = str(connection_parameters)

    try:
        zk = ZKAccess(connstr=connstr, device_model=ZK100)
        connected_devices[zk.handle] = zk
    except pyzkaccess.exceptions.ZKSDKError as e:
        return {
            "status": "error",
            "message": str(e),
        }

    return {"status": "success", "handle": zk.handle}


@app.post("/restart_device")
def restart_device(handle: int):
    try:
        response = connected_devices[handle].restart()
        return {"status": "success", "response": response}
    except KeyError as e:
        return {"status": "error", "message": "No connected device found with the given handle, try /connect"}

    except pyzkaccess.exceptions.ZKSDKError as e:
        return {
            "status": "error",
            "message": str(e),
        }


@app.post("/test_relay_unlock")
def test_relay_unlock(handle: int):
    try:
        response = connected_devices[handle].relays.lock.switch_on(5)
        return {"status": "success", "response": response}
    except KeyError as e:
        return {"status": "error", "message": "No connected device found with the given handle, try /connect"}

    except pyzkaccess.exceptions.ZKSDKError as e:
        return {
            "status": "error",
            "message": str(e),
        }


@app.get("/device_data")
def get_device_data(handle: int, tablename: TableName):
    data = connected_devices[handle].get_data(tablename)
    return data


@app.post("/device_data")
def set_device_data(params: SetDeviceDataParams):
    connected_devices[params.handle].set_data(params.tablename, params.data)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
