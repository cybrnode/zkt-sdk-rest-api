from app.exceptions import DeviceNotConnectedException

from starlette.requests import Request
from starlette.responses import JSONResponse
import pyzkaccess
import uvicorn
from fastapi import FastAPI
from .routers import devices

app = FastAPI()


app.include_router(devices.router)


@app.get("/")
async def no_hello_world():
    return {"message": "No Hello World"}


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


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
