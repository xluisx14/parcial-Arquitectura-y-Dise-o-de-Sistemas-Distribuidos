from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import PacienteORM
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError

async def get_paciente(db: AsyncSession, paciente_id: int):
    result = await db.execute(select(PacienteORM).where(PacienteORM.id == paciente_id))
    return result.scalars().first()

async def agregar_observacion(db: AsyncSession, paciente_id: int, observacion: str, usuario_nombre: str):
    paciente = await get_paciente(db, paciente_id)
    if not paciente:
        return None
    nueva_obs = f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M')} - {usuario_nombre}]\n{observacion}"
    paciente.observaciones = (paciente.observaciones or "") + nueva_obs
    await db.commit()
    return paciente

async def crear_paciente(db: AsyncSession, data: dict):
    try:
        # Convertir fecha_nacimiento de string a date
        fecha_nac_str = data.get("fecha_nacimiento")
        fecha_nac_date = None
        if fecha_nac_str:
            try:
                fecha_nac_date = datetime.strptime(fecha_nac_str, "%Y-%m-%d").date()
            except (ValueError, TypeError) as e:
                print(f"⚠️ Error al convertir fecha en crear_paciente: {fecha_nac_str} | Error: {e}")
                fecha_nac_date = None  # Continuar sin fecha si falla
        
        paciente = PacienteORM(
            tipo_documento=data.get("tipo_documento"),
            numero_documento=data.get("numero_documento"),
            primer_apellido=data.get("primer_apellido"),
            segundo_apellido=data.get("segundo_apellido"),
            primer_nombre=data.get("primer_nombre"),
            segundo_nombre=data.get("segundo_nombre"),
            fecha_nacimiento=fecha_nac_date,
            edad=data.get("edad"),
            sexo=data.get("sexo"),
            genero=data.get("genero"),
            grupo_sanguineo=data.get("grupo_sanguineo"),
            factor_rh=data.get("factor_rh"),
            estado_civil=data.get("estado_civil"),
            direccion_residencia=data.get("direccion_residencia"),
            municipio_ciudad=data.get("municipio_ciudad"),
            departamento=data.get("departamento"),
            telefono=data.get("telefono"),
            celular=data.get("celular"),
            correo_electronico=data.get("correo_electronico"),
            ocupacion=data.get("ocupacion"),
            entidad_pertenece=data.get("entidad_pertenece"),
            regimen_afiliacion=data.get("regimen_afiliacion"),
            tipo_usuario=data.get("tipo_usuario"),
            observaciones=data.get("observaciones"),
        )
        db.add(paciente)
        await db.commit()
        await db.refresh(paciente)
        return paciente
    except SQLAlchemyError as e:
        await db.rollback()
        print(f"Error al crear paciente: {e}")
        return None
