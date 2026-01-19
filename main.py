from fastapi import FastAPI
from contextlib import asynccontextmanager
from rotas import adocao, adotantes, animais, atendentes
from database import init_db, close_db #conexao com banco
from fastapi_pagination import add_pagination

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_db()

# FastAPI app instance
app = FastAPI(lifespan=lifespan)

# Rotas para Endpoints
app.include_router(adocao.router)
app.include_router(adotantes.router)
app.include_router(animais.router)
app.include_router(atendentes.router)
add_pagination(app)