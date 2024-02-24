import jwt

from fastapi import APIRouter, Depends, Response, Header, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from src.configurations.database import get_async_session
from src.configurations.settings import settings
from src.models.sellers import Seller
from src.schemas import IncomingAuth, Token

tokens_router = APIRouter(tags=["token"], prefix="/token")

DBSession = Annotated[AsyncSession, Depends(get_async_session)]

# New JWT token
@tokens_router.post("", response_model=Token, status_code=status.HTTP_200_OK)
async def authenticate(auth: IncomingAuth, session: DBSession, response: Response):
    seller = await session.execute(select(Seller).where(Seller.email==auth.email))
    seller = seller.scalar()
    if seller and seller.verify_password(auth.password.get_secret_value()):
        access_token = jwt.encode({"id": seller.id}, settings.jwt_secret, algorithm="HS256")
        return Token(access_token=access_token, token_type="bearer")
    return Response(headers={"WWW-Authenticate": "Bearer"}, status_code=status.HTTP_401_UNAUTHORIZED)

# Helper function to get the user with token
async def get_current_user(session: DBSession, authenticate: Annotated[str | None, Header()] = None):
    if authenticate is None:
        return None
    payload = jwt.decode(authenticate[7:], settings.jwt_secret, algorithms=["HS256"])
    if "id" not in payload:
        return None
    return await session.get(Seller, payload["id"])
