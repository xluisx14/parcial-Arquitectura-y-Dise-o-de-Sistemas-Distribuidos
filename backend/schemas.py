from pydantic import BaseModel, EmailStr
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str
    rol: str
    username: str

class TokenData(BaseModel):
    username: Optional[str] = None
    rol: Optional[str] = None

class UsuarioCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    rol: str
    nombre_completo: Optional[str] = None

class UsuarioResponse(BaseModel):
    id: int
    username: str
    email: str
    rol: str
    nombre_completo: Optional[str]
    activo: bool
    class Config:
        from_attributes = True
