from typing import Optional

from pydantic.main import BaseModel


class User(BaseModel):
    CardNo: int
    Pin: int
    Password: str
    Group: int
    StartTime: str
    EndTime: str
    SuperAuthorize: bool


class ConnectionParams(BaseModel):
    protocol: Optional[str] = "TCP"
    ip_address: str = "192.168.10.201"
    port: Optional[int] = 4370
    timeout: Optional[int] = 4000
    passwd: Optional[str] = ""

    def __str__(self):
        return f"protocol={self.protocol},ipaddress={self.ip_address},port={self.port},timeout={self.timeout},passwd={self.passwd}"


class SetDeviceDataParams(list):
    class Config:
        schema_extra = {
            "example": {
                "data": [
                    User(
                        **{
                            "CardNo": "15540203",
                            "Pin": "1",
                            "Password": "123",
                            "Group": "0",
                            "StartTime": "0",
                            "EndTime": "0",
                            "SuperAuthorize": "1",
                        }
                    )
                ],
            }
        }
