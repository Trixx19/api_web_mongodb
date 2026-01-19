from fastapi import APIRouter, HTTPException
from beanie import PydanticObjectId
from beanie.odm.fields import Link
from fastapi_pagination import Page, Params, paginate
from fastapi import Query
from fastapi_pagination.ext.beanie import apaginate
from datetime import date
from typing import Optional
from modelos import Animal, Adotante, Atendente, Adocao, AdocaoCreate, AdocaoResponse, AdocaoUpdate
from fastapi import Depends

#PUT /adocoes/{id} -> AdocaoUpdate
#GET com fetch_links=True -> AdocaoResponse
#POST /adocoes/ -> AdocaoCreate

router = APIRouter(prefix="/adocao", tags=["Adocao"])
#schemas especificos quando:

#(1)Nem todos os campos vêm do usuário - ex: automatico (data atual), regra de negócio (cliente nao controla cancelamento na criação)
# = cliente ñ enviar e nem alterar

#(2)Link(referência) tem tipos diferentes -> Link[T] = schema separado
# API recebe ObjectId -> Beanie converte para Link. 

#(3)Validação diferente ex: post vs put  
# put aceita parcial
# post exige completo

#(4)segurança
#Senha só no post não reaparece depois.

#POST /adocoes/ - Criar adoção - Schema específico
from beanie import PydanticObjectId
from fastapi import HTTPException

@router.post("/")
async def criar_adocao(dados: AdocaoCreate):
    #buscar se existem no bd
    animal = await Animal.get(dados.animal_id)
    if not animal:
        raise HTTPException(status_code=404,detail="Animal não encontrado")

    if animal.status_adocao:
        raise HTTPException(status_code=400,detail="Animal já foi adotado")

    adotante = await Adotante.get(dados.adotante_id)
    if not adotante:
        raise HTTPException(status_code=404,detail="Adotante não encontrado")

    atendentes = []
    for atendente_id in dados.atendentes_ids:
        atendente = await Atendente.get(atendente_id)
        if not atendente:
            raise HTTPException(status_code=404,detail=f"Atendente {atendente_id} não encontrado")
        atendentes.append(atendente)

    if not atendentes:
        raise HTTPException(status_code=400,detail="A adoção deve ter ao menos um atendente")

    # criar adoção
    adocao = Adocao(
        data_adocao=dados.data_adocao,
        descricao=dados.descricao,
        animal=animal,                 
        adotante=adotante,             
        atendentes=atendentes,         
        cancelamento=False #sempre falso
    )

    await adocao.insert()

    #atualizar vínculos
    animal.status_adocao = True
    animal.adocoes.append(adocao)

    adotante.adocoes.append(adocao)
    for a in atendentes:
        a.adocoes.append(adocao)
        await a.save()

    await animal.save()
    await adotante.save()

    return adocao

#GET /adocoes/canceladas - Adoções canceladas
@router.get("/canceladas")
async def adocoes_canceladas():
    return await Adocao.find(Adocao.cancelamento == True).to_list()

#DELETE /adocoes/{adocao_id}/cancelar- Cancelar adoção (soft delete)
@router.delete("/{adocao_id}/cancelar")
async def cancelar_adocao(adocao_id: str):
    adocao = await Adocao.get(adocao_id)
    adocao.cancelamento = True
    await adocao.save()
    return {"msg": "Adoção cancelada"}

# | GET | `/adocoes/` | Listar adoções |
@router.get("/adocoes/")
async def listar_adocoes():
    adocoes = await Adocao.find_all().to_list()
    return adocoes

# | GET | `/adocoes/relatorio/completo/ordenados` | Relatório completo de adoções |
@router.get("/relatorio/completo/ordenados", response_model=Page[AdocaoResponse])
async def relatorio_completo_adocoes() -> Page[AdocaoResponse]:
    try:
        # busca com links resolvidos e ordenação
        adocoes = await Adocao.find_all(fetch_links=True).sort("-data_adocao").to_list()

        items = []
        for adocao in adocoes:
            animal_id = str(adocao.animal.id)
            adotante_id = str(adocao.adotante.id)
            atendentes_ids = [str(at.id) for at in adocao.atendentes]

            items.append(
                AdocaoResponse(
                    data_adocao=adocao.data_adocao,
                    descricao=adocao.descricao,
                    animal_id=animal_id,
                    adotante_id=adotante_id,
                    atendentes_ids=atendentes_ids
                )
            )

        return paginate(items)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar relatório: {str(e)}")

# | PUT | `/adocoes/{adocao_id}` | Atualizar adoção | enviar so o que quer alterar
@router.put("/{adocao_id}", response_model=AdocaoResponse)
async def atualizar_adocao(adocao_id: PydanticObjectId, dados: AdocaoUpdate):
    adocao = await Adocao.get(adocao_id)

    if not adocao:
        raise HTTPException(status_code=404,detail="Adoção não encontrada")

    dados_update = dados.model_dump(exclude_unset=True)

    if not dados_update: #evitar update vazio
        raise HTTPException(status_code=400,detail="Nenhum campo fornecido para atualização")

    if adocao.cancelamento: #impedir edição de já adoção cancelada
        raise HTTPException(status_code=400,detail="Adoção cancelada não pode ser alterada")

    await adocao.set(dados_update)

    return AdocaoResponse(
        data_adocao=adocao.data_adocao,
        descricao=adocao.descricao,
        cancelamento=adocao.cancelamento
    )

# | GET | `/adocoes/ano/{ano}` | Adoções por ano |
@router.get("/ano/{ano}")
async def adocoes_por_ano(ano: int):
    inicio = date(ano, 1, 1)
    fim = date(ano, 12, 31)

    adocoes = await Adocao.find(
        Adocao.data_adocao >= inicio,
        Adocao.data_adocao <= fim
    ).to_list()

    return adocoes

# | GET | `/adocoes/id/{adocao_id}` | Buscar adoção por ID |
@router.get("/id/{adocao_id}")
async def buscar_adocao_por_id(adocao_id: PydanticObjectId):
    adocao = await Adocao.get(adocao_id, fetch_links=True)

    if not adocao:
        raise HTTPException(
            status_code=404,
            detail="Adoção não encontrada"
        )

    return adocao
