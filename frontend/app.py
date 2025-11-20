from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import httpx
#rom auth import router as auth_router  # 🔹 incluir router del backend

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# 🔹 Incluir router de auth del backend
#pp.include_router(auth_router, prefix="/auth")

# ============================
# PÁGINA PRINCIPAL - LOGIN
# ============================
@app.get("/", response_class=HTMLResponse)
@app.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})

# ============================
# PÁGINA DE REGISTRO (Frontend)
# ============================
@app.get("/register", response_class=HTMLResponse)
async def register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request, "error": None})   

# ============================
# VISTAS POR ROL
# ============================
@app.get("/paciente", response_class=HTMLResponse)
async def paciente(request: Request):
    return templates.TemplateResponse("paciente.html", {"request": request})

@app.get("/admisionista", response_class=HTMLResponse)
async def admisionista(request: Request):
    return templates.TemplateResponse("admisionista.html", {"request": request})

@app.get("/medico", response_class=HTMLResponse)
async def medico(request: Request):
    return templates.TemplateResponse("medico.html", {"request": request})

@app.get("/secretaria", response_class=HTMLResponse)
async def secretaria(request: Request):
    return templates.TemplateResponse("secretaria.html", {"request": request})
