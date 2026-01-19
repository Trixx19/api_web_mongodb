import asyncio
import os
import random
from datetime import date
from pymongo import AsyncMongoClient
from beanie import init_beanie
from dotenv import load_dotenv
from faker import Faker

from modelos import Animal, Adotante, Atendente, Adocao

load_dotenv()
fake = Faker("pt_BR")

async def seed():
    mongodb_uri = os.getenv("DATABASE_URL")

    if not mongodb_uri:
        raise RuntimeError("DATABASE_URL não encontrada no .env")

    client = AsyncMongoClient(mongodb_uri)
    db = client["pet_orphanage"]

    await init_beanie(
        database=db,
        document_models=[Animal, Adotante, Atendente, Adocao]
    )

    #limpa total
    await Animal.delete_all()
    await Adotante.delete_all()
    await Atendente.delete_all()
    await Adocao.delete_all()

    
    #atendentes
    atendentes = []
    for _ in range(15):
        atendente = Atendente(
            nome=fake.name()
        )
        await atendente.insert()
        atendentes.append(atendente)

    
    #adotantes
    
    adotantes = []
    for _ in range(15):
        adotante = Adotante(
            nome=fake.name(),
            contato=fake.phone_number(),
            endereco=fake.city(),
            preferencias=random.choice([
                "Cães de pequeno porte",
                "Gatos",
                "Animais idosos",
                "Sem preferência"
            ])
        )
        await adotante.insert()
        adotantes.append(adotante)

    
    #animais
    animais = []
    for _ in range(15):
        especie = random.choice(["Cachorro", "Gato"])

        animal = Animal(
            nome=fake.first_name(),
            especie=especie,
            idade=random.randint(1, 12),
            data_resgate=fake.date_between(start_date="-2y", end_date="today"),
            status_adocao=False
        )
        await animal.insert()
        animais.append(animal)

    
    #adoções
    for i in range(15):
        adocao = Adocao(
            data_adocao=fake.date_between(start_date="-1y", end_date="today"),
            descricao=fake.sentence(nb_words=8),
            animal=animais[i],
            adotante=adotantes[i],
            atendentes=[random.choice(atendentes)]
        )

        await adocao.insert()

        #vínculos inversos
        animais[i].adocoes.append(adocao)
        adotantes[i].adocoes.append(adocao)
        atendentes[i].adocoes.append(adocao)

        animais[i].status_adocao = True

        await animais[i].save()
        await adotantes[i].save()
        await atendentes[i].save()

    print("Banco MongoDB populado com dados fictícios (Faker) com sucesso.")

if __name__ == "__main__":
    asyncio.run(seed())
