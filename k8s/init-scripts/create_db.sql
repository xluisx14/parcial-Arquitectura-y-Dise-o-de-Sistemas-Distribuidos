-- ==========================================
-- 🔹 REINICIAR BASE DE DATOS DE HISTORIA_CLINICA
-- ==========================================

-- Eliminar tablas existentes si las hay
DROP TABLE IF EXISTS historia_clinica.cierre_historia CASCADE;
DROP TABLE IF EXISTS historia_clinica.atencion CASCADE;
DROP TABLE IF EXISTS historia_clinica.paciente CASCADE;
DROP TABLE IF EXISTS historia_clinica.profesional CASCADE;
DROP TABLE IF EXISTS historia_clinica.usuario CASCADE;

-- Crear esquema
CREATE SCHEMA IF NOT EXISTS historia_clinica;

-- ==========================================
-- 🔹 TABLA DE REFERENCIA: PACIENTE
-- ==========================================
CREATE TABLE historia_clinica.paciente (
    id SERIAL PRIMARY KEY,
    tipo_documento VARCHAR(20),
    numero_documento VARCHAR(50),
    primer_apellido VARCHAR(100),
    segundo_apellido VARCHAR(100),
    primer_nombre VARCHAR(100),
    segundo_nombre VARCHAR(100),
    fecha_nacimiento DATE,
    edad INT,
    sexo VARCHAR(10),
    genero VARCHAR(50),
    grupo_sanguineo VARCHAR(5),
    factor_rh VARCHAR(5),
    estado_civil VARCHAR(50),
    direccion_residencia TEXT,
    municipio_ciudad VARCHAR(100),
    departamento VARCHAR(100),
    telefono VARCHAR(50),
    celular VARCHAR(50),
    correo_electronico VARCHAR(150),
    ocupacion VARCHAR(100),
    entidad_pertenece VARCHAR(100),
    regimen_afiliacion VARCHAR(50),
    tipo_usuario VARCHAR(50)
);

-- Convertir en tabla de referencia
SELECT create_reference_table('historia_clinica.paciente');

-- ==========================================
-- 🔹 TABLA DISTRIBUIDA: ATENCION
-- ==========================================
CREATE TABLE historia_clinica.atencion (
    id SERIAL,
    paciente_id INT NOT NULL,
    fecha_hora_atencion TIMESTAMP,
    tipo_atencion VARCHAR(50),
    motivo_consulta TEXT,
    enfermedad_actual TEXT,
    antecedentes_personales TEXT,
    antecedentes_familiares TEXT,
    alergias TEXT,
    habitos TEXT,
    medicamentos_actuales TEXT,
    signos_vitales TEXT,
    examen_fisico_general TEXT,
    examen_fisico_sistemas TEXT,
    impresion_diagnostica TEXT,
    codigos_cie10 VARCHAR(100),
    conducta_plan_manejo TEXT,
    recomendaciones TEXT,
    medicos_interconsultados TEXT,
    procedimientos_realizados TEXT,
    resultados_examenes TEXT,
    diagnostico_definitivo TEXT,
    evolucion_medica TEXT,
    tratamiento_instaurado TEXT,
    formulacion_medica TEXT,
    educacion_paciente TEXT,
    referencia_contrareferencia TEXT,
    estado_egreso VARCHAR(50),
    PRIMARY KEY (id, paciente_id)
);

-- Convertir en tabla distribuida
SELECT create_distributed_table('historia_clinica.atencion', 'paciente_id');

-- ==========================================
-- 🔹 TABLA LOCAL: PROFESIONAL
-- ==========================================
CREATE TABLE historia_clinica.profesional (
    id SERIAL PRIMARY KEY,
    nombre_profesional VARCHAR(150),
    tipo_profesional VARCHAR(50),
    registro_medico VARCHAR(100),
    cargo_servicio VARCHAR(100),
    firma_profesional TEXT
);

-- ==========================================
-- 🔹 TABLA DISTRIBUIDA: CIERRE_HISTORIA
-- ==========================================
CREATE TABLE historia_clinica.cierre_historia (
    id SERIAL,
    atencion_id INT NOT NULL,
    firma_paciente TEXT,
    fecha_hora_cierre TIMESTAMP,
    responsable_registro VARCHAR(150),
    PRIMARY KEY (id, atencion_id)
);

-- Convertir en tabla distribuida
SELECT create_distributed_table('historia_clinica.cierre_historia', 'atencion_id');

-- ==========================================
-- 🔹 TABLA DE USUARIOS (para login y roles)
-- ==========================================
CREATE TABLE historia_clinica.usuario (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(150) UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    rol VARCHAR(20) NOT NULL, -- Roles: medico, admisionista, paciente, resultados
    nombre_completo VARCHAR(200),
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT NOW()
);

-- Insertar usuarios de ejemplo
INSERT INTO historia_clinica.usuario (username, email, hashed_password, rol, nombre_completo, activo)
VALUES 
('admin', 'admin@example.com', '<hash_admin>', 'admisionista', 'Administrador', true),
('medico1', 'medico1@example.com', '<hash_medico>', 'medico', 'Dr. Juan Perez', true),
('paciente1', 'paciente1@example.com', '<hash_paciente>', 'paciente', 'Carlos Gomez', true),
('resultados1', 'resultados1@example.com', '<hash_resultados>', 'resultados', 'Encargado Resultados', true);

-- ==========================================
-- 🔹 LISTADO DE TABLAS
-- ==========================================
-- Tablas distribuidas
SELECT * FROM citus_tables WHERE distribution_column IS NOT NULL;

-- Tablas de referencia
SELECT * FROM citus_tables WHERE distribution_column IS NULL;
