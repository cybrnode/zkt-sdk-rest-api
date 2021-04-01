from typing import Any, Dict, List, Mapping, Optional
from fastapi import Header

from pydantic.main import BaseModel
from pyzkaccess.data import TableName


class ConnectionParams(BaseModel):
    protocol: Optional[str] = "TCP"
    ip_address: str = "192.168.10.201"
    port: Optional[int] = 4370
    timeout: Optional[int] = 4000
    passwd: Optional[str] = ""

    def __str__(self):
        return f"protocol={self.protocol},ipaddress={self.ip_address},port={self.port},timeout={self.timeout},passwd={self.passwd}"


class SetDeviceDataParams(BaseModel):
    tablename: TableName
    data: List[Mapping[str, Any]]

    class Config:
        schema_extra = {
            "example": {
                "handle": 234124,
                "tablename": "user",
                "data": [
                    {
                        "CardNo": "15540203",
                        "Pin": "1",
                        "Password": "123",
                        "Group": "0",
                        "StartTime": "0",
                        "EndTime": "0",
                        "SuperAuthorize": "1",
                    }
                ],
            }
        }
