from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from asyncpg import UniqueViolationError
from datetime import datetime

from fastapi.templating import Jinja2Templates
# from fastapi.staticfiles import StaticFiles  # ❌ Ya no necesitamos esto

from database import get_db, engine
from auth import router as auth_router, get_current_active_user, require_role
from crud import get_paciente, agregar_observacion, crear_paciente  # <-- agregar crear_paciente
from schemas import Token, UsuarioResponse
from models import UsuarioORM
from fastapi import Form

# ==========================================================
# Inicialización
# ==========================================================
app = FastAPI(title="Sistema de Salud - OAuth2 + JWT")

# Solo templates, sin static
templates = Jinja2Templates(directory="templates")
# app.mount("/static", StaticFiles(directory="static"), name="static")  # ❌ Eliminado

# ==========================================================
# CORS
# ==========================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================================
# Routers de autenticación
# ==========================================================
app.include_router(auth_router, prefix="/auth")

# ==========================================================
# Eventos
# ==========================================================
@app.on_event("startup")
async def startup():
    print("🚀 Backend iniciado y conectado a Citus")

@app.on_event("shutdown")
async def shutdown():
    await engine.dispose()

# ==========================================================
# Rutas frontend (HTML) - templates solo para login/registro
# ==========================================================
@app.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register")
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

# ==========================================================
# Endpoints API
# ==========================================================
@app.get("/")
async def root():
    return {"status": "online", "version": "2.0.0"}

@app.get("/health")
async def health(db: AsyncSession = Depends(get_db)):
    try:
        await db.execute("SELECT 1")
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error de DB: {str(e)}")

@app.get("/users/me", response_model=UsuarioResponse)
async def me(current_user: UsuarioORM = Depends(get_current_active_user)):
    return current_user

# ==========================================================
# Pacientes
# ==========================================================
@app.get("/pacientes/{paciente_id}")
async def endpoint_get_paciente(
    paciente_id: int,
    current_user: UsuarioORM = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    paciente = await get_paciente(db, paciente_id)
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    return paciente

@app.post("/pacientes/observacion/{paciente_id}")
async def endpoint_observacion(
    paciente_id: int,
    observacion: str,
    current_user: UsuarioORM = Depends(require_role(["medico"])),
    db: AsyncSession = Depends(get_db)
):
    paciente = await agregar_observacion(
        db, paciente_id, observacion, current_user.nombre_completo
    )
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    return {"message": "Observación agregada"}

# Endpoint para crear paciente (con conversión de fecha correcta)
@app.post("/pacientes")
async def endpoint_crear_paciente(
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: UsuarioORM = Depends(require_role(["admisionista", "medico"]))
):
    fecha_str = data.get("fecha_nacimiento")
    fecha_date = None
    if fecha_str:
        try:
            fecha_date = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Fecha de nacimiento inválida")

    # Reemplazamos fecha string por objeto date en el dict
    data["fecha_nacimiento"] = fecha_date

    paciente = await crear_paciente(db, data)
    if not paciente:
        raise HTTPException(status_code=500, detail="Error al crear paciente")
    return {"message": "Paciente creado", "paciente_id": paciente.id}

# --- Nuevos endpoints para panel médico (CRUD de atención y cierre_historia) ---

@app.get("/medico/paciente/{paciente_id}/atenciones")
async def obtener_atenciones_paciente(
    paciente_id: int,
    current_user: UsuarioORM = Depends(require_role(["medico"])),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(AtencionORM).where(AtencionORM.paciente_id == paciente_id)
    )
    atenciones = result.scalars().all()
    return atenciones


@app.post("/medico/atencion")
async def crear_o_actualizar_atencion(
    atencion_id: int | None = Form(default=None),
    paciente_id: int = Form(...),
    fecha_hora_atencion: str = Form(...),  # ISO datetime string
    tipo_atencion: str = Form(...),
    motivo_consulta: str = Form(...),
    enfermedad_actual: str = Form(...),
    antecedentes_personales: str = Form(...),
    antecedentes_familiares: str = Form(...),
    alergias: str = Form(...),
    habitos: str = Form(...),
    current_user: UsuarioORM = Depends(require_role(["medico"])),
    db: AsyncSession = Depends(get_db),
):
    from datetime import datetime

    try:
        fecha_dt = datetime.fromisoformat(fecha_hora_atencion)
    except ValueError:
        raise HTTPException(status_code=400, detail="Fecha y hora inválida")

    if atencion_id:
        atencion = await db.get(AtencionORM, atencion_id)
        if not atencion:
            raise HTTPException(status_code=404, detail="Atención no encontrada")
        # actualizar campos
        atencion.fecha_hora_atencion = fecha_dt
        atencion.tipo_atencion = tipo_atencion
        atencion.motivo_consulta = motivo_consulta
        atencion.enfermedad_actual = enfermedad_actual
        atencion.antecedentes_personales = antecedentes_personales
        atencion.antecedentes_familiares = antecedentes_familiares
        atencion.alergias = alergias
        atencion.habitos = habitos
    else:
        atencion = AtencionORM(
            paciente_id=paciente_id,
            fecha_hora_atencion=fecha_dt,
            tipo_atencion=tipo_atencion,
            motivo_consulta=motivo_consulta,
            enfermedad_actual=enfermedad_actual,
            antecedentes_personales=antecedentes_personales,
            antecedentes_familiares=antecedentes_familiares,
            alergias=alergias,
            habitos=habitos,
        )
        db.add(atencion)

    await db.commit()
    return {"message": "Atención guardada", "atencion_id": atencion.id}


@app.post("/medico/cierre_historia")
async def crear_o_actualizar_cierre_historia(
    id: int | None = Form(default=None),
    atencion_id: int = Form(...),
    firma_paciente: str = Form(""),
    fecha_hora_cierre: str = Form(...),  # ISO datetime string
    responsable_registro: str = Form(...),
    current_user: UsuarioORM = Depends(require_role(["medico"])),
    db: AsyncSession = Depends(get_db),
):
    from datetime import datetime

    try:
        fecha_cierre_dt = datetime.fromisoformat(fecha_hora_cierre)
    except ValueError:
        raise HTTPException(status_code=400, detail="Fecha de cierre inválida")

    if id:
        cierre = await db.get(CierreHistoriaORM, id)
        if not cierre:
            raise HTTPException(status_code=404, detail="Cierre de historia no encontrado")
        cierre.firma_paciente = firma_paciente
        cierre.fecha_hora_cierre = fecha_cierre_dt
        cierre.responsable_registro = responsable_registro
    else:
        cierre = CierreHistoriaORM(
            atencion_id=atencion_id,
            firma_paciente=firma_paciente,
            fecha_hora_cierre=fecha_cierre_dt,
            responsable_registro=responsable_registro,
        )
        db.add(cierre)

    await db.commit()
    return {"message": "Cierre de historia guardado", "cierre_id": cierre.id}

# ==========================================================
# Registro seguro
# ==========================================================
@app.post("/auth/register-safe")
async def register_safe(
    username: str,
    email: str,
    nombre_completo: str,
    rol: str,
    password: str,
    db: AsyncSession = Depends(get_db)
):
    from auth import crear_usuario
    
    try:
        user = await crear_usuario(db, username, email, nombre_completo, rol, password)
        await db.commit()
        return {"message": "Usuario creado", "user_id": user.id}
    except IntegrityError as e:
        await db.rollback()
        if isinstance(e.orig, UniqueViolationError):
            raise HTTPException(status_code=400, detail="Usuario o email ya existe")
        raise HTTPException(status_code=500, detail="Error inesperado al crear usuario")