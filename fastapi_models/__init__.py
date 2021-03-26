from typing import Optional

from pydantic.main import BaseModel


class ConnectionParams(BaseModel):
    protocol: Optional[str] = "TCP"
    ip_address: str = "192.168.10.201"
    port: Optional[int] = 4370
    timeout: Optional[int] = 4000
    passwd: Optional[str] = ""

    def __str__(self):
        return f"protocol={self.protocol},ipaddress={self.ip_address},port={self.port},timeout={self.timeout},passwd={self.passwd}"


class DeviceHandleParam(BaseModel):
    handle: int
