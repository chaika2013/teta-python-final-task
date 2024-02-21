import pytest
from fastapi import status
from sqlalchemy import select

from src.models import books, sellers


# Тест на ручку создающую книгу
@pytest.mark.asyncio
async def test_create_book(db_session, async_client):
    seller = sellers.Seller(first_name="Alex", last_name="Bukin", email="bukin@yahoo.com", password="password1")
    db_session.add_all([seller])
    await db_session.flush()

    data = {"title": "Wrong Code", "author": "Robert Martin", "count_pages": 104, "year": 2007, "seller_id": seller.id}
    response = await async_client.post("/api/v1/books/", json=data)

    assert response.status_code == status.HTTP_201_CREATED

    result_data = response.json()

    all_books = await db_session.execute(select(books.Book))
    res = all_books.scalars().all()
    assert len(res) == 1

    assert result_data == {
        "id": res[0].id,
        "title": "Wrong Code",
        "author": "Robert Martin",
        "count_pages": 104,
        "year": 2007,
        "seller_id": seller.id,
    }


# Тест на ручку получения списка книг
@pytest.mark.asyncio
async def test_get_books(db_session, async_client):
    seller = sellers.Seller(first_name="Alex", last_name="Bukin", email="bukin@yahoo.com", password="password1")
    db_session.add_all([seller])
    await db_session.flush()

    # Создаем книги вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке
    book = books.Book(author="Pushkin", title="Eugeny Onegin", year=2001, count_pages=104, seller_id=seller.id)
    book_2 = books.Book(author="Lermontov", title="Mziri", year=1997, count_pages=104, seller_id=seller.id)
    db_session.add_all([seller, book, book_2])
    await db_session.flush()

    response = await async_client.get("/api/v1/books/")

    assert response.status_code == status.HTTP_200_OK

    assert len(response.json()["books"]) == 2  # Опасный паттерн! Если в БД есть данные, то тест упадет

    # Проверяем интерфейс ответа, на который у нас есть контракт.
    assert response.json() == {
        "books": [
            {"title": "Eugeny Onegin", "author": "Pushkin", "year": 2001, "id": book.id, "count_pages": 104, "seller_id": seller.id},
            {"title": "Mziri", "author": "Lermontov", "year": 1997, "id": book_2.id, "count_pages": 104, "seller_id": seller.id},
        ]
    }


# Тест на ручку получения одной книги
@pytest.mark.asyncio
async def test_get_single_book(db_session, async_client):
    seller = sellers.Seller(first_name="Alex", last_name="Bukin", email="bukin@yahoo.com", password="password1")
    db_session.add_all([seller])
    await db_session.flush()

    # Создаем книги вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке
    book = books.Book(author="Pushkin", title="Eugeny Onegin", year=2001, count_pages=104, seller_id=seller.id)
    book_2 = books.Book(author="Lermontov", title="Mziri", year=1997, count_pages=104, seller_id=seller.id)

    db_session.add_all([book, book_2])
    await db_session.flush()

    response = await async_client.get(f"/api/v1/books/{book.id}")

    assert response.status_code == status.HTTP_200_OK

    # Проверяем интерфейс ответа, на который у нас есть контракт.
    assert response.json() == {
        "title": "Eugeny Onegin",
        "author": "Pushkin",
        "year": 2001,
        "count_pages": 104,
        "id": book.id,
        "seller_id": seller.id,
    }


# Тест на ручку удаления книги
@pytest.mark.asyncio
async def test_delete_book(db_session, async_client):
    seller = sellers.Seller(first_name="Alex", last_name="Bukin", email="bukin@yahoo.com", password="password1")
    db_session.add_all([seller])
    await db_session.flush()

    # Создаем книги вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке
    book = books.Book(author="Pushkin", title="Eugeny Onegin", year=2001, count_pages=104, seller_id=seller.id)

    db_session.add(book)
    await db_session.flush()

    response = await async_client.delete(f"/api/v1/books/{book.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    await db_session.flush()

    all_books = await db_session.execute(select(books.Book))
    res = all_books.scalars().all()
    assert len(res) == 0


# Тест на ручку обновления книги
@pytest.mark.asyncio
async def test_update_book(db_session, async_client):
    seller1 = sellers.Seller(first_name="Alex", last_name="Bukin", email="bukin@yahoo.com", password="password1")
    seller2 = sellers.Seller(first_name="Nick", last_name="Lemming", email="lemming@gmail.com", password="password2")
    db_session.add_all([seller1, seller2])
    await db_session.flush()

    # Создаем книги вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке
    book = books.Book(author="Pushkin", title="Eugeny Onegin", year=2001, count_pages=104, seller_id=seller1.id)

    db_session.add(book)
    await db_session.flush()

    response = await async_client.put(
        f"/api/v1/books/{book.id}",
        json={"title": "Mziri", "author": "Lermontov", "count_pages": 100, "year": 2007, "seller_id": seller2.id},
    )

    assert response.status_code == status.HTTP_200_OK
    await db_session.flush()

    # Проверяем, что обновились все поля
    res = await db_session.get(books.Book, book.id)
    assert res.title == "Mziri"
    assert res.author == "Lermontov"
    assert res.count_pages == 100
    assert res.year == 2007
    assert res.seller_id == seller2.id

@pytest.mark.asyncio
async def test_get_book_not_found(async_client):
    """
    Test GET /book/id when there is no such id.
    """
    response = await async_client.get("/api/v1/books/12345")
    assert response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_delete_book_not_found(async_client):
    """
    Test DELETE /book/id when there is no such id.
    """
    response = await async_client.delete("/api/v1/books/12345")
    assert response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_create_book_seller_not_found(db_session, async_client):
    data = {"title": "Wrong Code", "author": "Robert Martin", "count_pages": 104, "year": 2007, "seller_id": 12345}
    response = await async_client.post("/api/v1/books/", json=data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.asyncio
async def test_update_book_seller_not_found(db_session, async_client):
    seller = sellers.Seller(first_name="Alex", last_name="Bukin", email="bukin@yahoo.com", password="password1")
    db_session.add_all([seller])
    await db_session.flush()

    # Создаем книги вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке
    book = books.Book(author="Pushkin", title="Eugeny Onegin", year=2001, count_pages=104, seller_id=seller.id)

    db_session.add(book)
    await db_session.flush()

    response = await async_client.put(
        f"/api/v1/books/{book.id}",
        json={"title": "Mziri", "author": "Lermontov", "count_pages": 100, "year": 2007, "seller_id": 12345},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
