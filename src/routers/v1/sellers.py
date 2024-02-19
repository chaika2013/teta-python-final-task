from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from src.configurations.database import get_async_session
from src.models.sellers import Seller
from src.schemas import ReturnedAllSellers, ReturnedSeller, IncomingSeller

sellers_router = APIRouter(tags=["sellers"], prefix="/sellers")

DBSession = Annotated[AsyncSession, Depends(get_async_session)]

# Return all sellers
@sellers_router.get("/", response_model=ReturnedAllSellers)
async def get_all_sellers(session: DBSession):
    query = select(Seller)
    res = await session.execute(query)
    books = res.scalars().all()
    return {"sellers": books}

# Return seller by ID
@sellers_router.get("/{seller_id}", response_model=ReturnedSeller)
async def get_seller(seller_id: int, session: DBSession):
    res = await session.get(Seller, seller_id)
    return res

# Add new seller
@sellers_router.post("/", response_model=ReturnedSeller, status_code=status.HTTP_201_CREATED)  # Прописываем модель ответа
async def create_seller(
    seller: IncomingSeller, session: DBSession
):
    new_seller = Seller(
        first_name=seller.first_name,
        last_name=seller.last_name,
        email=seller.email,
        password=seller.password.get_secret_value(),
    )
    session.add(new_seller)
    await session.flush()

    return new_seller

# Delete seller by id
@sellers_router.delete("/{seller_id}")
async def delete_seller(seller_id: int, session: DBSession):
    deleted_seller = await session.get(Seller, seller_id)
    if deleted_seller:
        await session.delete(deleted_seller)
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    return Response(status_code=status.HTTP_404_NOT_FOUND)

# Update by seller id
@sellers_router.put("/{seller_id}")
async def update_book(seller_id: int, new_data: IncomingSeller, session: DBSession):
    if updated_seller := await session.get(Seller, seller_id):
        updated_seller.first_name = new_data.first_name
        updated_seller.last_name = new_data.last_name
        updated_seller.email = new_data.email
        updated_seller.password = new_data.password.get_secret_value()

        await session.flush()

        return updated_seller

    return Response(status_code=status.HTTP_404_NOT_FOUND)
