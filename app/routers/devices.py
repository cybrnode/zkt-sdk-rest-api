from starlette.responses import HTMLResponse, JSONResponse
from app.exceptions import DeviceNotConnectedException
from typing import Any, Dict, List, Mapping

from fastapi import APIRouter

from app.models import ConnectionParams

from pyzkaccess import ZKAccess
import pyzkaccess
from pyzkaccess.common import DeviceDataFilter
from pyzkaccess.data import DeviceParametersEnum, TableName, User
from pyzkaccess.device import ZK400


router = APIRouter(prefix="/devices")


# TODO: see if there's a better way for this, maybe using an in-memory database?
# Though we might not need to; as this app doesn't need to be scalable

# This is a dict: key is the connection handle and value is a ZKAccess connected object

connected_devices: Dict[int, ZKAccess] = dict()


def get_connected_device(handle: int) -> ZKAccess:
    try:
        return connected_devices[handle]
    except KeyError:
        raise DeviceNotConnectedException(handle)


@router.post("/connect")
def connect(connection_parameters: ConnectionParams):
    connstr = connection_parameters.__str__()

    try:
        zk = ZKAccess(connstr=connstr, device_model=ZK400)
        if not zk.handle:
            raise Exception("Unexpected error: handle not valid")

        connected_devices[zk.handle] = zk
    except pyzkaccess.exceptions.ZKSDKError as e:
        return JSONResponse(
            content={
                "status": "error",
                "message": str(e),
            },
            status_code=400,
        )

    return {"status": "success", "handle": zk.handle}


@router.post("/{handle}/restart")
def restart_device(handle: int):
    get_connected_device(handle).restart()
    return {"status": "success", "message": "Device restarted successfully"}


@router.get("/{handle}/config/doors")
def get_device_doors(handle: int):
    door_numbers_list = [door.number for door in get_connected_device(handle).doors]  # type: ignore
    return door_numbers_list


@router.post("/{handle}/tests/relay/unlock")
def test_relay_unlock(handle: int):
    get_connected_device(handle).relays.lock.switch_on(5)
    return {"status": "success", "message": "relay unlock successfully"}


@router.get("/{handle}/param/{param_name}")
def get_device_param(param_name: DeviceParametersEnum, handle: int):
    param = get_connected_device(handle).parameters.__getattribute__(param_name)
    return str(param)


@router.put("/{handle}/param")
def set_device_param(updated_params: Mapping[DeviceParametersEnum, Any], handle: int):

    for k, v in updated_params.items():
        get_connected_device(handle).parameters.__setattr__(k, v)
    return {"status": "success", "message": "parameter updated successfully"}


@router.get("/{handle}/data/{tablename}")
def get_device_data(tablename: TableName, handle: int):
    data = get_connected_device(handle).get_data(tablename)
    return data


@router.post("/{handle}/data/{tablename}")
def set_device_data(data: List[Mapping[str, Any]], handle: int, tablename: TableName):
    get_connected_device(handle).set_data(tablename, data)
    return {"status": "success", "message": "data updated successfully"}


@router.delete("/{handle}/data/")
def delete_all_data(handle: int):
    for tablename in TableName:
        device_data = get_connected_device(handle).sdk.get_device_data(tablename, 1024 * 1024 * 4)

        i: Any
        for i in device_data:
            get_connected_device(handle).sdk.delete_device_data(tablename, [i])

    return {"status": "success", "message": "all device data deleted successfully"}


@router.delete("/{handle}/data/{tablename}")
def delete_device_data(data_filter: Mapping[str, Any], handle: int, tablename: TableName):
    device_data_filter = DeviceDataFilter()
    for k, v in data_filter.items():
        device_data_filter.add_condition(k, v)

    get_connected_device(handle).sdk.delete_device_data(tablename, [device_data_filter])
    return {"status": "success", "message": "data deleted successfully"}


@router.get("/{handle}/users", response_model=List[User])
def get_all_users(handle: int):
    all_users = get_connected_device(handle).get_all_users()
    return all_users


@router.get("/{handle}/users/{pin}", response_model=User)
def get_user_by_pin(handle: int, pin: int):
    user = get_connected_device(handle).get_user_by_pin(pin)
    return user


@router.put("/{handle}/users/{pin}")
def update_user_by_pin(handle: int, pin: int, updated_user: User):
    print(updated_user)
    get_connected_device(handle).update_user_by_pin(pin, updated_user)
    return {"status": "success", "message": "User added successfully"}


@router.delete("/{handle}/users/{pin}")
def delete_user_by_pin(handle: int, pin: int):
    get_connected_device(handle).delete_user_by_pin(pin)
    return {"status": "success", "message": "user deleted successfully"}


@router.post("/{handle}/users")
def add_user(users: List[User], handle: int):
    get_connected_device(handle).add_users(users)
    return {"status": "success", "message": "User added successfully"}


html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://localhost:8000/devices/<PLACE_HANDLE_HERE>/realtimelogs");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


@router.get("/testwebsockets")
async def get(handle: int):
    return HTMLResponse(html.replace("<PLACE_HANDLE_HERE>", str(handle)))
