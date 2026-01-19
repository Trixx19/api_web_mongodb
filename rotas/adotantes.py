from fastapi import APIRouter, HTTPException, Query
from typing import List
from datetime import date
from modelos import Adotante, AdotanteUpdate

router = APIRouter(prefix="/adotantes", tags=["Adotantes"])

# | POST | `/adotantes/` | Criar adotante |
@router.post("/")
async def criar_adotante(adotante: Adotante):
    await adotante.insert()
    return adotante

# | GET | `/adotantes/` | Listar adotantes |
@router.get("/")
async def listar_adotantes():
    adotantes = await Adotante.find_all().to_list()
    return adotantes

# | GET | `/adotantes/buscar/nome` | Buscar adotante por nome |
@router.get("/buscar/nome")
async def buscar_adotante_por_nome(
    nome: str = Query(..., description="Nome (ou parte do nome)")):
    adotantes = await Adotante.find({"nome": {"$regex": nome, "$options": "i"}}).to_list()

    return adotantes

# | GET | `/adotantes/{adotante_id}` | Buscar adotante por ID |
@router.get("/{adotante_id}")
async def buscar_adotante_por_id(adotante_id: str):
    adotante = await Adotante.get(adotante_id)

    if not adotante: raise HTTPException(status_code=404,detail="Adotante não encontrado")

    return adotante

# | PUT | `/adotantes/{adotante_id}` | Atualizar adotante |
@router.put("/{adotante_id}", response_model=Adotante)
async def atualizar_adotante(adotante_id: str, dados: AdotanteUpdate):
    adotante = await Adotante.get(adotante_id)

    if not adotante:
        raise HTTPException(status_code=404, detail="Adotante não encontrado")

    # Atualiza apenas os campos enviados
    update_data = dados.model_dump(exclude_unset=True)
    if update_data:
        await adotante.set(update_data)

    return adotante

# | DELETE | `/adotantes/{adotante_id}` | Deletar adotante |
@router.delete("/{adotante_id}")
async def deletar_adotante(adotante_id: str):
    adotante = await Adotante.get(adotante_id)

    if not adotante:raise HTTPException(status_code=404, detail="Adotante não encontrado")

    await adotante.delete()
    return {"msg": "Adotante removido com sucesso"}
