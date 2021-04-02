from app.exceptions import DeviceNotConnectedException
from typing import Dict, List
from fastapi import APIRouter

from app.api_models import ConnectionParams, SetDeviceDataParams

from pyzkaccess import ZKAccess, ZK100
import pyzkaccess
from pyzkaccess.data import TableName, User


router = APIRouter(prefix="/devices")


# TODO: see if there's a better way for this, maybe using an in-memory database?
# Though we might not need to as this app doesn't need to be scalable

# This is a dict key is the connection handle and value is a ZKAccess connected object

connected_devices: Dict[int, ZKAccess] = dict()


def get_connected_device(handle: int) -> ZKAccess:
    try:
        return connected_devices[handle]
    except KeyError:
        raise DeviceNotConnectedException(handle)


@router.post("/connect")
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


@router.post("/{handle}/restart")
def restart_device(handle):
    response = get_connected_device(handle).restart()
    return {"status": "success", "response": response}


@router.post("/{handle}/tests/relay/unlock")
def test_relay_unlock(handle):
    response = get_connected_device(handle).relays.lock.switch_on(5)
    return {"status": "success", "response": response}


@router.get("/{handle}/data")
def get_device_data(tablename: TableName, handle):
    data = get_connected_device(handle).get_data(tablename)
    return data


@router.post("/{handle}/data")
def set_device_data(params: SetDeviceDataParams, handle):
    get_connected_device(handle).set_data(params.tablename, params.data)


@router.get("/{handle}/users", response_model=List[User])
def get_all_users(handle):
    all_users = get_connected_device(handle).get_users()
    return all_users


@router.post("/{handle}/users")
def add_user(users: List[User], handle):  # TODO: see if there's a better way to only specify handle param once for the whole app
    get_connected_device(handle).add_users(users)
