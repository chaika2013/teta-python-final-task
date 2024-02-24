from pydantic import BaseModel, EmailStr, SecretStr

__all__ = ["IncomingAuth", "Token"]

class IncomingAuth(BaseModel):
    email: EmailStr
    password: SecretStr

class Token(BaseModel):
    access_token: str
    token_type: str

