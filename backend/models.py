from sqlalchemy import (
    Column, Integer, String, Date, DateTime, Boolean,
    Table, ForeignKey, Text
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


usuario_rol_table = Table(
    "usuario_rol",
    Base.metadata,
    Column("usuario_id", Integer, ForeignKey("historia_clinica.usuario.id"), primary_key=True),
    Column("rol_id", Integer, ForeignKey("historia_clinica.rol.id"), primary_key=True),
    schema="historia_clinica"
)


class UsuarioORM(Base):
    __tablename__ = "usuario"
    __table_args__ = {"schema": "historia_clinica"}

    id = Column(Integer, primary_key=True, index=True)

    paciente = relationship("PacienteORM", back_populates="usuario", uselist=False)
    profesional = relationship("ProfesionalORM", back_populates="usuario", uselist=False)
    
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    nombre_completo = Column(String(200))
    activo = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())

    roles = relationship(
        "RolORM",
        secondary=usuario_rol_table,
        back_populates="usuarios",
        lazy="selectin"
    )


class RolORM(Base):
    __tablename__ = "rol"
    __table_args__ = {"schema": "historia_clinica"}

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), unique=True, nullable=False)

    usuarios = relationship(
        "UsuarioORM",
        secondary=usuario_rol_table,
        back_populates="roles",
        lazy="selectin"
    )


class PacienteORM(Base):
    __tablename__ = "paciente"
    __table_args__ = {"schema": "historia_clinica"}

    id = Column(Integer, primary_key=True, index=True)

    tipo_documento = Column(String(20))
    numero_documento = Column(String(50), unique=True, index=True)

    primer_apellido = Column(String(100))
    segundo_apellido = Column(String(100))

    primer_nombre = Column(String(100))
    segundo_nombre = Column(String(100))

    fecha_nacimiento = Column(Date)
    edad = Column(Integer)  # Si calculas edad en backend

    sexo = Column(String(20))
    genero = Column(String(50))
    grupo_sanguineo = Column(String(5))
    factor_rh = Column(String(5))
    estado_civil = Column(String(50))

    direccion_residencia = Column(String(200))
    municipio_ciudad = Column(String(100))
    departamento = Column(String(100))

    telefono = Column(String(50))
    celular = Column(String(50))
    correo_electronico = Column(String(150))

    ocupacion = Column(String(150))
    entidad_pertenece = Column(String(150))
    regimen_afiliacion = Column(String(50))
    tipo_usuario = Column(String(50))

    observaciones = Column(Text)  # Aquí el médico agrega observaciones

    usuario_id = Column(Integer, ForeignKey("historia_clinica.usuario.id"), unique=True, nullable=True)
    usuario = relationship("UsuarioORM", back_populates="paciente", uselist=False)


class ProfesionalORM(Base):
    __tablename__ = "profesional"
    __table_args__ = {"schema": "historia_clinica"}

    id = Column(Integer, primary_key=True, index=True)

    nombre_profesional = Column(String(200))
    tipo_profesional = Column(String(100))
    registro_medico = Column(String(100))
    cargo_servicio = Column(String(150))
    firma_profesional = Column(String(150))

    usuario_id = Column(Integer, ForeignKey("historia_clinica.usuario.id"), unique=True, nullable=True)
    usuario = relationship("UsuarioORM", back_populates="profesional", uselist=False)


class AtencionORM(Base):
    __tablename__ = "atencion"
    __table_args__ = {"schema": "historia_clinica"}

    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(Integer, ForeignKey("historia_clinica.paciente.id"), nullable=False)
    fecha_hora_atencion = Column(DateTime)
    tipo_atencion = Column(String(50))
    motivo_consulta = Column(Text)
    enfermedad_actual = Column(Text)
    antecedentes_personales = Column(Text)
    antecedentes_familiares = Column(Text)
    alergias = Column(Text)
    habitos = Column(Text)
    # agregar aquí los demás campos necesarios

    paciente = relationship("PacienteORM", back_populates="atenciones")


class CierreHistoriaORM(Base):
    __tablename__ = "cierre_historia"
    __table_args__ = {"schema": "historia_clinica"}

    id = Column(Integer, primary_key=True, index=True)
    atencion_id = Column(Integer, ForeignKey("historia_clinica.atencion.id"), nullable=False)
    firma_paciente = Column(Text)
    fecha_hora_cierre = Column(DateTime)
    responsable_registro = Column(String(150))

    atencion = relationship("AtencionORM", back_populates="cierre_historia")


PacienteORM.atenciones = relationship("AtencionORM", back_populates="paciente", cascade="all, delete-orphan")
AtencionORM.cierre_historia = relationship("CierreHistoriaORM", back_populates="atencion", uselist=False)


ROLES = {
    "medico": "Puede registrar observaciones y actualizar atención",
    "admisionista": "Gestiona ingresos",
    "paciente": "Solo consulta",
    "secretaria": "Puede exportar en PDF"
}