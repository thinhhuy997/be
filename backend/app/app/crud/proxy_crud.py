from app.schemas.proxy_schema import IProxyCreate, IProxyUpdate
from datetime import datetime
from app.crud.base_crud import CRUDBase
from app.models.proxy_model import Proxy
from sqlmodel import select, func, and_, col
from sqlmodel.ext.asyncio.session import AsyncSession


class CRUDProxy(CRUDBase[Proxy, IProxyCreate, IProxyUpdate]):

    async def get_count_of_proxies(
        self,
        *,

        start_time: datetime,
        end_time: datetime,
        db_session: AsyncSession | None = None,
    ) -> int:
        db_session = db_session or super().get_db().session
        subquery = (
            select(Proxy)
            .where(
                and_(
                    Proxy.created_at > start_time,
                    Proxy.created_at < end_time,
                )
            )
            .subquery()
        )
        query = select(func.count()).select_from(subquery)
        count = await db_session.execute(query)
        value = count.scalar_one_or_none()
        return value
    

proxy = CRUDProxy(Proxy)
