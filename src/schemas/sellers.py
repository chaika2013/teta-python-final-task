from typing import List
from pydantic import BaseModel, Field, EmailStr, SecretStr
from .books import ReturnedBookWithoutSeller

__all__ = ["BaseSeller", "IncomingSeller", "ReturnedAllSellers", "ReturnedSeller", "ReturnedSellerWithBooks"]

class BaseSeller(BaseModel):
    first_name: str = Field(..., min_length=1)
    last_name: str = Field(..., min_length=1)
    email: EmailStr

class IncomingSeller(BaseSeller):
    password: SecretStr = Field(..., min_length=8)

class ReturnedSeller(BaseSeller):
    id: int

class ReturnedSellerWithBooks(ReturnedSeller):
    books: List[ReturnedBookWithoutSeller]

class ReturnedAllSellers(BaseModel):
    sellers: list[ReturnedSeller]
