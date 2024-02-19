from pydantic import BaseModel, Field, EmailStr, SecretStr

__all__ = ["IncomingSeller", "ReturnedAllSellers", "ReturnedSeller"]

class BaseSeller(BaseModel):
    first_name: str = Field(..., min_length=1)
    last_name: str = Field(..., min_length=1)
    email: EmailStr

class IncomingSeller(BaseSeller):
    password: SecretStr = Field(..., min_length=8)

class ReturnedSeller(BaseSeller):
    id: int

class ReturnedAllSellers(BaseModel):
    sellers: list[ReturnedSeller]
