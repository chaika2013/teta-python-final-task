import pytest

from fastapi import status
from sqlalchemy import select

from src.models import sellers

@pytest.mark.asyncio
async def test_create_seller(async_client):
    data = {"first_name": "Alex", "last_name": "Bukin", "email": "bukin@yahoo.com", "password": "password"}
    response = await async_client.post("/api/v1/seller", json=data)

    assert response.status_code == status.HTTP_201_CREATED

    result_data = response.json()

    assert result_data == {
        "id": 1,
        "first_name": "Alex",
        "last_name": "Bukin",
        "email": "bukin@yahoo.com",
    }

@pytest.mark.asyncio
async def test_create_seller_bad_format(async_client):
    data = {"first_name": "Alex", "last_name": "Bukin", "email": "bukin@yahoo.com", "password": "password"}
    for (key, val) in [("first_name", ""), ("last_name", ""), ("email", "agasdf"), ("password", "shrtpwd")]:
        bad_data = data.copy()
        bad_data[key] = val
        response = await async_client.post("/api/v1/seller", json=bad_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

@pytest.mark.asyncio
async def test_get_sellers(db_session, async_client):
    seller1 = sellers.Seller(first_name="Alex", last_name="Bukin", email="bukin@yahoo.com", password="password1")
    seller2 = sellers.Seller(first_name="Nick", last_name="Lemming", email="lemming@gmail.com", password="password2")

    db_session.add_all([seller1, seller2])
    await db_session.flush()

    response = await async_client.get("/api/v1/seller")

    assert response.status_code == status.HTTP_200_OK

    assert len(response.json()["sellers"]) == 2

    assert response.json() == {
        "sellers": [
            {"id": seller1.id, "first_name": "Alex", "last_name": "Bukin", "email": "bukin@yahoo.com"},
            {"id": seller2.id, "first_name": "Nick", "last_name": "Lemming", "email": "lemming@gmail.com"},
        ]
    }

@pytest.mark.asyncio
async def test_get_seller_by_id(db_session, async_client):
    seller1 = sellers.Seller(first_name="Alex", last_name="Bukin", email="bukin@yahoo.com", password="password1")
    seller2 = sellers.Seller(first_name="Nick", last_name="Lemming", email="lemming@gmail.com", password="password2")

    db_session.add_all([seller1, seller2])
    await db_session.flush()

    response = await async_client.get(f"/api/v1/seller/{seller1.id}")

    assert response.status_code == status.HTTP_200_OK

    assert response.json() == {
        "id": seller1.id,
        "first_name": "Alex",
        "last_name": "Bukin",
        "email": "bukin@yahoo.com",
    }

@pytest.mark.asyncio
async def test_delete_seller(db_session, async_client):
    seller = sellers.Seller(first_name="Alex", last_name="Bukin", email="bukin@yahoo.com", password="password1")

    db_session.add(seller)
    await db_session.flush()

    response = await async_client.delete(f"/api/v1/seller/{seller.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    await db_session.flush()

    all_books = await db_session.execute(select(sellers.Seller))
    res = all_books.scalars().all()
    assert len(res) == 0

@pytest.mark.asyncio
async def test_delete_seller_not_found(db_session, async_client):
    response = await async_client.delete("/api/v1/seller/12345")
    assert response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_update_seller(db_session, async_client):
    seller = sellers.Seller(first_name="Alex", last_name="Bukin", email="bukin@yahoo.com", password="password1")

    db_session.add(seller)
    await db_session.flush()

    response = await async_client.put(
        f"/api/v1/seller/{seller.id}",
        json={"first_name": "Nick", "last_name": "Lemming", "email": "lemming@gmail.com", "password": "password2"},
    )

    assert response.status_code == status.HTTP_200_OK
    await db_session.flush()

    res = await db_session.get(sellers.Seller, seller.id)
    assert res.first_name == "Nick"
    assert res.last_name == "Lemming"
    assert res.email == "lemming@gmail.com"
    assert res.password == "password2"

@pytest.mark.asyncio
async def test_update_seller_not_found(db_session, async_client):
    response = await async_client.put(
        f"/api/v1/seller/12345",
        json={"first_name": "Nick", "last_name": "Lemming", "email": "lemming@gmail.com", "password": "password2"},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
