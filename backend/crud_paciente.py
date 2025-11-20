from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from models import PacienteORM
from sqlalchemy.exc import SQLAlchemyError


async def crear_paciente(db: AsyncSession, data: dict):
    try:
        fecha_nacimiento = data.get("fecha_nacimiento")
        fecha_date = None
        if fecha_nacimiento:
            fecha_date = datetime.strptime(fecha_nacimiento, "%Y-%m-%d").date()

        paciente = PacienteORM(
            tipo_documento=data.get("tipo_documento"),
            numero_documento=data.get("numero_documento"),
            primer_apellido=data.get("primer_apellido"),
            segundo_apellido=data.get("segundo_apellido"),
            primer_nombre=data.get("primer_nombre"),
            segundo_nombre=data.get("segundo_nombre"),
            fecha_nacimiento=fecha_date,  # ahora es date, no str
            # elimina edad, genero, grupo_sanguineo, factor_rh, estado_civil si no existen en modelo
            sexo=data.get("sexo"),
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
        )

        db.add(paciente)
        await db.commit()
        await db.refresh(paciente)

        return paciente

    except SQLAlchemyError as e:
        await db.rollback()
        print(f"Error al crear paciente: {e}")
        return None
