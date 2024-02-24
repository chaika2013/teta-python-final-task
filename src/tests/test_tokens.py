import pytest

from fastapi import status

from src.models import sellers

@pytest.mark.asyncio
async def test_create_token(db_session, async_client):
    seller = sellers.Seller(first_name="Alex", last_name="Bukin", email="bukin@yahoo.com")
    seller.set_password("password1")
    db_session.add(seller)
    await db_session.flush()

    data = {"email": "bukin@yahoo.com", "password": "password1"}
    response = await async_client.post("/api/v1/token", json=data)

    assert response.status_code == status.HTTP_200_OK

    result_data = response.json()
    assert ("access_token" in result_data)
    assert result_data['token_type'] == "bearer"

@pytest.mark.asyncio
async def test_create_token_wrong_password(db_session, async_client):
    seller = sellers.Seller(first_name="Alex", last_name="Bukin", email="bukin@yahoo.com")
    seller.set_password("password1")
    db_session.add(seller)
    await db_session.flush()

    data = {"email": "bukin@yahoo.com", "password": "123456"}
    response = await async_client.post("/api/v1/token", json=data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.asyncio
async def test_create_token_wrong_email(db_session, async_client):
    seller = sellers.Seller(first_name="Alex", last_name="Bukin", email="bukin@yahoo.com")
    seller.set_password("password1")
    db_session.add(seller)
    await db_session.flush()

    data = {"email": "bukin@gmail.com", "password": "password1"}
    response = await async_client.post("/api/v1/token", json=data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
