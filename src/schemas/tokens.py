from pydantic import BaseModel, EmailStr, SecretStr

__all__ = ["IncomingAuth", "ReturnedToken"]

class IncomingAuth(BaseModel):
    email: EmailStr
    password: SecretStr

class ReturnedToken(BaseModel):
    jwt: str

