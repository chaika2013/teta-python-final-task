import jwt

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from src.configurations.database import get_async_session
from src.configurations.settings import settings
from src.models.sellers import Seller
from src.schemas import IncomingAuth, ReturnedToken

tokens_router = APIRouter(tags=["token"], prefix="/token")

DBSession = Annotated[AsyncSession, Depends(get_async_session)]

# New JWT token
@tokens_router.post("", response_model=ReturnedToken, status_code=status.HTTP_200_OK)
async def authenticate(auth: IncomingAuth, session: DBSession, response: Response):
    seller = await session.execute(select(Seller).where(Seller.email==auth.email))
    seller = seller.scalar()
    if seller and seller.verify_password(auth.password.get_secret_value()):
        encoded_jwt = jwt.encode({"id": seller.id}, settings.jwt_secret, algorithm="HS256")
        return {"jwt": encoded_jwt}
    return Response(status_code=status.HTTP_401_UNAUTHORIZED)
