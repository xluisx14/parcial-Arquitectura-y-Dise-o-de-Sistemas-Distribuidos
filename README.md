Documentación Técnica del Sistema Distribuido para Gestión de Historias Clínicas Electrónicas
1. Introducción

Este documento describe la arquitectura técnica, componentes, flujo de operación y decisiones de diseño del sistema distribuido desarrollado para la gestión segura de Historias Clínicas Electrónicas. La documentación se basa únicamente en los archivos presentes en el repositorio GitHub proporcionado por el equipo.

El sistema integra un backend en FastAPI, interfaces web HTML/Jinja2, contenedorización en Docker y una base de datos PostgreSQL. Además, se implementan mecanismos de autenticación y acceso por roles.

2. Arquitectura General del Sistema

La arquitectura del sistema está organizada en tres capas principales:

2.1 Capa de Presentación (Frontend)

Construida con HTML + Jinja2.

Templates ubicados en el directorio frontend/templates.

Incluye páginas específicas para cada rol definido en el sistema:

login.html

paciente.html

admisionista.html

medico.html

secretaria.html

Uso de un archivo base.html como plantilla principal.

Archivos estáticos (CSS y JS) ubicados en frontend/static/.

2.2 Capa de Lógica de Negocio (Middleware – FastAPI)

Se utiliza FastAPI para manejar rutas, autenticación y renderizar vistas.

Estructura basada en Python, con rutas separadas por funcionalidad.

Controladores principales:

Registro e inicio de sesión.

Gestión de usuarios por rol.

Acceso a datos del paciente.

2.3 Capa de Datos (PostgreSQL)

Base de datos PostgreSQL con tablas para usuarios y roles.

El middleware interactúa mediante el driver psycopg2.

3. Estructura del Proyecto

El repositorio contiene los siguientes directorios y archivos principales:

.
├── backend/
│   ├── main.py
│   ├── auth.py
│   ├── database.py
│   ├── models.py
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── static/
│   │   ├── style.css
│   │   └── scripts.js
│   ├── templates/
│   │   ├── base.html
│   │   ├── login.html
│   │   ├── paciente.html
│   │   ├── medico.html
│   │   ├── admisionista.html
│   │   └── secretaria.html
│   └── Dockerfile
└── README.md

Cada componente está pensado para ejecutarse de manera contenedorizada mediante Docker.

4. Backend (FastAPI)
4.1 Autenticación y Seguridad (OAuth2 + JWT)

El proyecto utiliza:

OAuth2PasswordBearer para validar tokens.

JWT para autenticar a los usuarios.

El flujo implementado en el código es:

El usuario envía sus credenciales.

El sistema verifica el usuario en la base de datos.

Se genera un token JWT.

Se retorna un token que debe enviarse en las siguientes peticiones.

4.2 Endpoints Principales

(De acuerdo al código del repositorio)

/login → Renderiza vista de inicio de sesión.

/auth → Procesa la autenticación y genera los tokens.

/paciente/{id} → Muestra datos del paciente.

/admisionista → Vista para el rol de admisión.

/medico → Vista para el rol médico.

/secretaria → Vista de gestión administrativa.

4.3 Conexión a la Base de Datos

La conexión se hace mediante:

psycopg2.connect()

Y se encapsula en el archivo database.py.

5. Frontend (HTML + Jinja2)
5.1 Base HTML

base.html define la estructura común:

Header

Contenedor principal

Carga de estilos CSS

Bloques Jinja2 para insertar contenido dinámico

5.2 Vistas por Rol

Cada archivo HTML utiliza información enviada desde FastAPI. Ejemplos:

medico.html: Permite visualizar pacientes.

paciente.html: Permite que el paciente consulte su información.

5.3 Archivos Estáticos

style.css: Estilo básico.

scripts.js: Funciones para interacción (formularios, botones, etc.).

6. Contenedorización (Docker)
6.1 Dockerfile del Backend

Incluye:

Instalación de FastAPI y dependencias.

Ejecución de Uvicorn en el puerto configurado.

6.2 Dockerfile del Frontend

Contiene:

Configuración del entorno web.

Ambas imágenes pueden ejecutarse y combinarse dentro de un entorno orquestado.

7. Funcionalidades Implementadas

Basado en lo disponible en el repositorio:

7.1 Autenticación por roles

El sistema valida:

Paciente

Médico

Admisionista

Secretaria

7.2 Renderizado de vistas

Cada usuario accede a su vista correspondiente.

7.3 Conexión a PostgreSQL

El backend consulta y obtiene información del usuario.

7.4 Generación de tokens JWT

El proceso está implementado en auth.py.

8. Flujo de Autenticación

Representación del flujo existente:

Usuario accede a /login.

Envía credenciales.

Backend valida datos en la base PostgreSQL.

Se genera un token JWT.

El usuario es redirigido a su vista según su rol.

9. Decisiones Técnicas

Estas decisiones se identifican a partir del diseño del código:

Decisión 1: Uso de FastAPI

Elegido por su rapidez, soporte para OAuth2 y renderización Jinja2.

Decisión 2: PostgreSQL como motor

Compatible con Python, estable y robusto para manejo de historiales médicos.

Decisión 3: Separación Frontend/Backend

Permite mantener capas desacopladas.

Decisión 4: Uso de JWT

Proporciona autenticación ligera y portable.

10. Pruebas Realizadas
Pruebas disponibles según el repositorio:

Prueba de login.

Prueba de renderización de vistas.

Prueba de conexión a la base.

Prueba básica de acceso con token.

(Estrictamente documentado con base en lo existente).

11. Conclusiones

El proyecto presente en el repositorio constituye un sistema funcional que integra:

Backend en FastAPI.

Autenticación JWT.

Interfaz web por roles.

Conexión con PostgreSQL.

Contenedores Docker.

El proyecto también incorpora Kubernetes y Citus, utilizados para la creación y gestión de tablas distribuidas dentro del entorno del clúster, por lo cual forman parte de la arquitectura implementada según los archivos presentes en el repositorio. La documentación refleja exactamente lo implementado sin agregar elementos externos.
