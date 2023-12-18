from sqlmodel import Field, Relationship, SQLModel
from app.models.base_uuid_model import BaseUUIDModel
from uuid import UUID

# ip, port, user, pass

class ProxyBase(SQLModel):
    ip: str = Field(index=True)
    port: str
    username: str
    password: str

class Proxy(BaseUUIDModel, ProxyBase, table=True):
    # pass
    created_by_id: UUID | None = Field(default=None, foreign_key="User.id")
    created_by: "User" = Relationship(  # noqa: F821
        sa_relationship_kwargs={
            "lazy": "joined",
            "primaryjoin": "Proxy.created_by_id==User.id",
        }
    )