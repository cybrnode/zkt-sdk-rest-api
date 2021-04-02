class DeviceNotConnectedException(Exception):
    def __init__(self, handle) -> None:
        self.handle = handle
