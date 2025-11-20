from fastapi import APIRouter, HTTPException, Depends, Form, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert
from database import get_db
from models import UsuarioORM, RolORM, usuario_rol_table, PacienteORM, ProfesionalORM
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext

SECRET_KEY = "tu_secreto_aqui"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_password_hash(password: str):
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str):
    return pwd_context.verify(password, hashed)


def create_access_token(data: dict, expires_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# ---------------------------------------------------------
#   LOGIN
# ---------------------------------------------------------
@router.post("/login")
async def login(
    email: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(select(UsuarioORM).where(UsuarioORM.email == email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    # Obtener el rol del usuario
    result_roles = await db.execute(
        select(RolORM.nombre)
        .join(usuario_rol_table, RolORM.id == usuario_rol_table.c.rol_id)
        .where(usuario_rol_table.c.usuario_id == user.id)
    )
    roles = [r[0] for r in result_roles.all()]
    rol = roles[0] if roles else "paciente"

    token = create_access_token({"sub": str(user.id)})

    return {"access_token": token, "token_type": "bearer", "rol": rol}


# ---------------------------------------------------------
#   DECODIFICAR TOKEN Y OBTENER USUARIO
# ---------------------------------------------------------
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")

        if user_id is None:
            raise HTTPException(status_code=401, detail="Token inválido")

        result = await db.execute(select(UsuarioORM).where(UsuarioORM.id == int(user_id)))
        user = result.scalar_one_or_none()

    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

    if user is None:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")

    return user


async def get_current_active_user(
    user: UsuarioORM = Depends(get_current_user)
):
    return user


# ---------------------------------------------------------
#   REQUIRE ROLE
# ---------------------------------------------------------
def require_role(required_roles):
    if isinstance(required_roles, str):
        required_roles = [required_roles]  # normalizar

    async def checker(
        user: UsuarioORM = Depends(get_current_active_user),
        db: AsyncSession = Depends(get_db)
    ):
        q = await db.execute(
            select(RolORM.nombre)
            .join(usuario_rol_table, RolORM.id == usuario_rol_table.c.rol_id)
            .where(usuario_rol_table.c.usuario_id == user.id)
        )
        roles_usuario = [r[0] for r in q.all()]

        # validar si tiene algún rol permitido
        if not any(r in roles_usuario for r in required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para acceder"
            )

        return user

    return checker


# ---------------------------------------------------------
#   REGISTRO
# ---------------------------------------------------------
@router.post("/register")
async def register_user(
    username: str = Form(...),
    email: str = Form(...),
    nombre_completo: str = Form(...),
    rol: str = Form(...),
    password: str = Form(...),

    tipo_documento: str = Form(None),
    numero_documento: str = Form(None),
    primer_apellido: str = Form(None),
    segundo_apellido: str = Form(None),
    primer_nombre: str = Form(None),
    segundo_nombre: str = Form(None),
    fecha_nacimiento: str = Form(None),
    sexo: str = Form(None),
    direccion_residencia: str = Form(None),
    municipio_ciudad: str = Form(None),
    departamento: str = Form(None),
    telefono: str = Form(None),
    celular: str = Form(None),
    correo_electronico: str = Form(None),
    ocupacion: str = Form(None),
    entidad_pertenece: str = Form(None),
    regimen_afiliacion: str = Form(None),
    tipo_usuario: str = Form(None),

    tipo_profesional: str = Form(None),
    registro_medico: str = Form(None),
    cargo_servicio: str = Form(None),
    firma_profesional: str = Form(None),

    db: AsyncSession = Depends(get_db)
):

    # validar email existente
    result = await db.execute(select(UsuarioORM).where(UsuarioORM.email == email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Ya existe un usuario con ese email")

    # crear usuario
    # Determinar nombre completo: preferir el campo enviado, sino construirlo desde los nombres/apellidos
    nombre_completo_final = (nombre_completo or "").strip()
    if not nombre_completo_final:
        nombre_completo_final = " ".join(filter(None, [primer_nombre, segundo_nombre, primer_apellido, segundo_apellido])).strip()
    if not nombre_completo_final:
        # como último recurso usar el username
        nombre_completo_final = username

    new_user = UsuarioORM(
        username=username,
        email=email,
        nombre_completo=nombre_completo_final,
        hashed_password=get_password_hash(password)
    )
    db.add(new_user)
    await db.flush()

    # asignar rol
    rol_normalizado = rol.lower().strip()
    result = await db.execute(select(RolORM).where(RolORM.nombre == rol_normalizado))
    rol_obj = result.scalar_one_or_none()

    if not rol_obj:
        rol_obj = RolORM(nombre=rol_normalizado)
        db.add(rol_obj)
        await db.flush()

    await db.execute(
        insert(usuario_rol_table).values(
            usuario_id=new_user.id,
            rol_id=rol_obj.id
        )
    )

    # si el usuario es paciente → crear PacienteORM
    if rol_normalizado == "paciente":
        # Convertir fecha_nacimiento de string a date
        fecha_nac_date = None
        if fecha_nacimiento:
            try:
                fecha_nac_date = datetime.strptime(fecha_nacimiento, "%Y-%m-%d").date()
            except (ValueError, TypeError) as e:
                print(f"⚠️ Error al convertir fecha: {fecha_nacimiento} | Error: {e}")
                raise HTTPException(status_code=400, detail=f"Fecha de nacimiento inválida: {fecha_nacimiento}")
        
        paciente = PacienteORM(
            tipo_documento=tipo_documento,
            numero_documento=numero_documento,
            primer_apellido=primer_apellido,
            segundo_apellido=segundo_apellido,
            primer_nombre=primer_nombre,
            segundo_nombre=segundo_nombre,
            fecha_nacimiento=fecha_nac_date,
            sexo=sexo,
            direccion_residencia=direccion_residencia,
            municipio_ciudad=municipio_ciudad,
            departamento=departamento,
            telefono=telefono,
            celular=celular,
            correo_electronico=correo_electronico or email,
            ocupacion=ocupacion,
            entidad_pertenece=entidad_pertenece,
            regimen_afiliacion=regimen_afiliacion,
            # Heredar tipo_usuario desde el campo enviado o desde el rol si no se envía
            tipo_usuario=(tipo_usuario or rol_normalizado),
            usuario_id=new_user.id,
        )

        db.add(paciente)

    # si el usuario es médico → crear ProfesionalORM
    elif rol_normalizado == "medico":
        profesional = ProfesionalORM(
            nombre_profesional=nombre_completo_final,
            tipo_profesional=tipo_profesional,
            registro_medico=registro_medico,
            cargo_servicio=cargo_servicio,
            firma_profesional=firma_profesional,
            usuario_id=new_user.id,
        )

        db.add(profesional)

    await db.commit()

    return {"message": "Usuario registrado correctamente"}