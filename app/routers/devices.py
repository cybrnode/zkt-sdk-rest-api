from fastapi.params import Header
from typing import Any, List, Mapping

from fastapi import APIRouter


from pyzkaccess import ZKAccess
from pyzkaccess.common import DeviceDataFilter
from pyzkaccess.data import DeviceParametersEnum, TableName, User
from pyzkaccess.device import ZK400


router = APIRouter(prefix="/devices")


def zk_device(connection_string):
    ZKAccess(connstr=connection_string, device_model=ZK400)


@router.post("/test_connection")
def test_connection(connection_string: str = Header(...)):
    zk_device(connection_string)
    return {
        "status": "success",
        "message": "connected successfully",
    }


@router.post("/restart")
def restart_device(connection_string: str = Header(...)):
    with zk_device(connection_string) as zk:
        zk.restart()

    return {"status": "success", "message": "Device restarted successfully"}


@router.get("/config/doors")
def get_device_doors(connection_string: str = Header(...)):
    with zk_device(connection_string) as zk:
        door_numbers_list = [door.number for door in zk.doors]  # type: ignore
    return door_numbers_list


@router.post("/tests/relay/unlock")
def test_relay_unlock(connection_string: str = Header(...)):
    with zk_device(connection_string) as zk:
        zk.relays.lock.switch_on(5)
    return {"status": "success", "message": "relay unlock successfully"}


@router.get("/param/{param_name}")
def get_device_param(param_name: DeviceParametersEnum, connection_string: str = Header(...)):
    with zk_device(connection_string) as zk:
        param = zk.parameters.__getattribute__(param_name)

    return str(param)


@router.put("/param")
def set_device_param(updated_params: Mapping[DeviceParametersEnum, Any], connection_string: str = Header(...)):
    with zk_device(connection_string) as zk:
        for k, v in updated_params.items():
            zk.parameters.__setattr__(k, v)

    return {"status": "success", "message": "parameter updated successfully"}


@router.get("/data/{tablename}")
def get_device_data(tablename: TableName, connection_string: str = Header(...)):

    with zk_device(connection_string) as zk:
        data = zk.get_data(tablename)

    return data


@router.post("/data/{tablename}")
def set_device_data(data: List[Mapping[str, Any]], tablename: TableName, connection_string: str = Header(...)):
    with zk_device(connection_string) as zk:
        zk.set_data(tablename, data)

    return {"status": "success", "message": "data updated successfully"}


@router.delete("/data/")
def delete_all_data(connection_string: str = Header(...)):
    with zk_device(connection_string) as zk:

        for tablename in TableName:
            device_data = zk.sdk.get_device_data(tablename, 1024 * 1024 * 4)

            i: Any
            for i in device_data:
                zk.sdk.delete_device_data(tablename, [i])

    return {"status": "success", "message": "all device data deleted successfully"}


@router.delete("/data/{tablename}")
def delete_device_data(data_filter: Mapping[str, Any], tablename: TableName, connection_string: str = Header(...)):
    with zk_device(connection_string) as zk:
        device_data_filter = DeviceDataFilter()
        for k, v in data_filter.items():
            device_data_filter.add_condition(k, v)

        zk.sdk.delete_device_data(tablename, [device_data_filter])
    return {"status": "success", "message": "data deleted successfully"}


@router.get("/users", response_model=List[User])
def get_all_users(connection_string: str = Header(...)):
    with zk_device(connection_string) as zk:
        all_users = zk.get_all_users()
    return all_users


@router.get("/users/{pin}", response_model=User)
def get_user_by_pin(pin: int, connection_string: str = Header(...)):
    with zk_device(connection_string) as zk:
        user = zk.get_user_by_pin(pin)
    return user


@router.put("/users/{pin}")
def update_user_by_pin(pin: int, updated_user: User, connection_string: str = Header(...)):
    with zk_device(connection_string) as zk:
        zk.update_user_by_pin(pin, updated_user)
    return {"status": "success", "message": "User added successfully"}


@router.delete("/users/{pin}")
def delete_user_by_pin(pin: int, connection_string: str = Header(...)):
    with zk_device(connection_string) as zk:
        zk.delete_user_by_pin(pin)
    return {"status": "success", "message": "user deleted successfully"}


@router.post("/users")
def add_user(users: List[User], connection_string: str = Header(...)):
    with zk_device(connection_string) as zk:
        zk.add_users(users)
    return {"status": "success", "message": "User added successfully"}
