from app.models.proxy_model import ProxyBase
from app.models.user_model import UserBase
# from backend.app.app.schemas.common_schema import IPagination
from sqlmodel import SQLModel, Relationship
from app.utils.partial import optional
from uuid import UUID
from pydantic import BaseModel, validator


class IProxyCreate(ProxyBase):
    pass

@optional
class IProxyUpdate(ProxyBase):
    pass

class IProxyRead(ProxyBase):
    id: UUID

class IproxyIndex(SQLModel):
    ip_index: int
    port_index: int
    username_index: int
    password_index: int

# class dfsd(IPagination):
#     pass

class IProxyWithCreatedByUser(IProxyRead):
    created_by: UserBase | None