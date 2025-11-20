import asyncio
from passlib.context import CryptContext
from sqlalchemy import select
from database import async_session
from models import UsuarioORM

# Configuración de hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# Usuarios y contraseñas
usuarios = [
    {"username": "admin", "email": "admin@example.com", "password": "admin123", "rol": "admisionista", "nombre_completo": "Administrador"},
    {"username": "medico1", "email": "medico1@example.com", "password": "medico123", "rol": "medico", "nombre_completo": "Dr. Juan Perez"},
    {"username": "paciente1", "email": "paciente1@example.com", "password": "paciente123", "rol": "paciente", "nombre_completo": "Carlos Gomez"},
    {"username": "secretaria1", "email": "secretaria1@example.com", "password": "secretaria123", "rol": "secretaria", "nombre_completo": "Encargada PDF"},
]

async def main():
    async with async_session() as session:
        for u in usuarios:
            hashed = get_password_hash(u["password"])
            
            result = await session.execute(
                select(UsuarioORM).filter_by(username=u["username"])
            )
            user_obj = result.scalars().first()

            if user_obj:
                user_obj.hashed_password = hashed
                print(f"🔄 Actualizado hash de: {u['username']}")
            else:
                new_user = UsuarioORM(
                    username=u["username"],
                    email=u["email"],
                    hashed_password=hashed,
                    rol=u["rol"],
                    nombre_completo=u["nombre_completo"],
                    activo=True
                )
                session.add(new_user)
                print(f"✅ Creado usuario: {u['username']}")
        
        await session.commit()
        print("🎯 Todos los hashes han sido guardados en la base de datos.")

if __name__ == "__main__":
    asyncio.run(main())
