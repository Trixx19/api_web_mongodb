
from beanie import Document, Link
from beanie.odm.fields import PydanticObjectId
from pydantic import Field, BaseModel
from datetime import date
from typing import Optional
#Document(beanie): Entity + persistence
#pydantic model, persisted in MongoDB, automatic _id, has database methods: .save .get(id), .find()

#BaseModel (Pydantic): DTO (data transfer object)
# Validation only; used for request/response schemas (body validation)
    
#AniAdocaoAtendAdot para request/response body?

class Atendente(Document):
    nome: str 
    adocoes: list[Link["Adocao"]] = Field(default_factory=list)

    class Settings:
        name = "atendentes"

class Animal(Document):
    nome: str
    especie: str
    idade: int
    data_resgate: date
    status_adocao: bool = False
    
    adocoes: list[Link["Adocao"]] = Field(default_factory=list)

    class Settings:
        name = "animais"

class AdotanteUpdate(BaseModel):
    nome: Optional[str]
    contato: Optional[str]
    endereco: Optional[str]
    preferencias: Optional[str]

class Adotante(Document):
    nome: str
    contato: str
    endereco: str
    preferencias: str
    
    adocoes: list[Link["Adocao"]] = Field(default_factory=list)
    
    class Settings:
        name = "adotantes"

class Adocao(Document):
    data_adocao: date
    descricao: str
    cancelamento: bool = False

    animal: Link["Animal"] #só 1
    adotante: Link["Adotante"] #só 1
    atendentes: list[Link["Atendente"]] = Field(default_factory=list)

    class Settings:
        name = "adocoes"

class AdocaoCreate(BaseModel):
    data_adocao: date = Field(..., example="2024-05-10")
    descricao: str = Field(..., example="Adoção responsável")

    animal_nome: str = Field(...,example="Lara",description="Nome do animal (obter via GET /animais)")
    adotante_nome: str = Field(..., example="Pedro Miguel Sales",description="Nome do adotante (obter via GET /adotantes)")
    atendentes_nomes: list[str] = Field(...,example=["Miguel Melo", "Enzo Gabriel Marques"], description="Lista de nomes dos atendentes (GET /atendentes)")

class AdocaoResponse(BaseModel):
    data_adocao: date
    descricao: str
    animal_id: str   
    adotante_id: str        
    atendentes_ids: list[str] = []     

class AdocaoUpdate(BaseModel):
    descricao: Optional[str]

class AtendenteUpdate(BaseModel):
    nome: str
    contato: str
    endereco: str