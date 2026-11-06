
"""Aplicação para o módulo de extensão DevOps."""

from contextlib import asynccontextmanager
from datetime import datetime, timezone
from functools import lru_cache
from typing import Annotated, List
import os

from fastapi import FastAPI, Depends
from sqlmodel import SQLModel, Session, create_engine, select

from .modelo import Tarefa


@lru_cache
def obter_engine():
    """Cria e retorna a conexão com o banco de dados MySQL."""

    database_username = os.environ.get("DATABASE_USERNAME")
    database_password = os.environ.get("DATABASE_PASSWORD")
    database_address = os.environ.get("DATABASE_ADDRESS")
    database = os.environ.get("DATABASE")

    configuracoes = {
        "DATABASE_USERNAME": database_username,
        "DATABASE_PASSWORD": database_password,
        "DATABASE_ADDRESS": database_address,
        "DATABASE": database,
    }

    for nome, valor in configuracoes.items():
        if not valor:
            raise RuntimeError(f"{nome} está faltando")

    return create_engine(
        f"postgresql+psycopg://{database_username}:{database_password}"
        f"@{database_address}/{database}"
    )


def criar_sessao():
    """Função utilitária para criar sessão no banco de dados."""

    with Session(obter_engine()) as sessao:
        yield sessao


SESSAO = Annotated[Session, Depends(criar_sessao)]


@asynccontextmanager
async def inicializacao(_: FastAPI):
    """Função para inicialização da API e do banco de dados."""

    SQLModel.metadata.create_all(obter_engine())
    yield


APP = FastAPI(lifespan=inicializacao)


# GET /tarefas: Lista todas as tarefas
@APP.get("/tarefas")
async def tarefas(sessao: SESSAO) -> List[Tarefa]:
    """Rota para listar as tarefas."""

    lista_tarefas = sessao.exec(select(Tarefa).offset(0)).all()

    return lista_tarefas


# POST /tarefas: Cria tarefa
@APP.post("/tarefas", status_code=201)
async def post_tarefa(
    sessao: SESSAO,
    titulo: str,
    descricao: str = None
):
    """Rota para criar uma tarefa."""

    data = datetime.now().astimezone(timezone.utc).replace(microsecond=0)

    tarefa_nova = Tarefa(
        titulo=titulo,
        descricao=descricao,
        data_criacao=data,
    )

    sessao.add(tarefa_nova)
    sessao.commit()
    sessao.refresh(tarefa_nova)

    return {"mensagem": "OK"}


# GET /tarefas/{id_tarefa}: Visualiza tarefa específica
@APP.get("/tarefas/{id_tarefa}")
async def tarefa_especifica(sessao: SESSAO, id_tarefa: int) -> Tarefa:
    """Rota para visualizar uma tarefa específica."""

    regra = select(Tarefa).where(Tarefa.id == id_tarefa)
    resultado = sessao.exec(regra).all()

    if resultado:
        return resultado[0]

    return {"mensagem": "Tarefa não existe"}


# PUT /tarefas/{id_tarefa}: Atualiza tarefa específica
@APP.put("/tarefas/{id_tarefa}")
async def concluir_tarefa(sessao: SESSAO, id_tarefa: int):
    """Rota para concluir uma tarefa."""

    regra = select(Tarefa).where(Tarefa.id == id_tarefa)
    resultado = sessao.exec(regra).all()

    if not resultado:
        return {"mensagem": "Tarefa não existe"}

    if resultado[0].concluida is True:
        return {"mensagem": "Tarefa já finalizada"}

    resultado[0].finalizar()

    sessao.add(resultado[0])
    sessao.commit()
    sessao.refresh(resultado[0])

    return {"mensagem": "Tarefa atualizada"}


# DELETE /tarefas/{id_tarefa}: Exclui tarefa
@APP.delete("/tarefas/{id_tarefa}")
async def apagar_tarefa(sessao: SESSAO, id_tarefa: int):
    """Rota para apagar tarefa."""

    regra = select(Tarefa).where(Tarefa.id == id_tarefa)
    resultado = sessao.exec(regra).all()

    if not resultado:
        return {"mensagem": "Tarefa não existe"}

    tarefa = resultado[0]

    sessao.delete(tarefa)
    sessao.commit()

    return {"mensagem": "Tarefa removida"}


# GET /: Rota inicial
@APP.get("/")
async def index():
    """Rota raiz."""

    return {"mensagem": "Olá, mundo!"}


# GET /autor: Retorna o autor da aplicação
@APP.get("/autor")
async def autor():
    """Rota para retornar o autor da aplicação."""

    return {"mensagem": "Gisele Ferreira da Silva"}
