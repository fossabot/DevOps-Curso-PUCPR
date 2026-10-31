"""Aplicação para o módulo de extensão DevOps"""
import sys
import os
from datetime import datetime, timezone
from typing import Annotated
from fastapi import FastAPI, Depends
from sqlmodel import SQLModel, Session, create_engine, select
from app.modelo import Tarefa

DATABASE_USERNAME = os.environ.get("DATABASE_USERNAME")
DATABASE_PASSWORD = os.environ.get("DATABASE_PASSWORD")
DATABASE_ADDRESS = os.environ.get("DATABASE_ADDRESS")
DATABASE = os.environ.get("DATABASE")

if DATABASE_USERNAME is None:
    print("DATABASE_USERNAME está faltando")
    sys.exit(1)
if DATABASE_PASSWORD is None:
    print("DATABASE_PASSWORD está faltando")
    sys.exit(1)
if DATABASE_ADDRESS is None:
    print("DATABASE_ADDRESS está faltando")
    sys.exit(1)
if DATABASE is None:
    print("DATABASE está faltando")
    sys.exit(1)

URL_BANCO = (
    f"mysql+pymysql://{DATABASE_USERNAME}:{DATABASE_PASSWORD}"
    f"@{DATABASE_ADDRESS}:3306/{DATABASE}"
)
ENGINE = create_engine(URL_BANCO)

def criar_sessao():
    """Cria uma sessão de banco de dados."""
    with Session(ENGINE) as s:
        yield s

SESSAO = Annotated[Session, Depends(criar_sessao)]

async def inicializacao(_api: FastAPI):
    """Função para inicializar a API com o banco de dados."""
    print("Iniciando a API...")
    SQLModel.metadata.create_all(ENGINE)
    yield
    print("Finalizando...")

APP = FastAPI(lifespan=inicializacao)
TAREFAS = []

# GET /tarefas: Lista todas as tarefas (somente id e titulo)
@APP.get("/tarefas")
async def tarefas(sessao: SESSAO) -> list[Tarefa]:
    """Rota para listar as tarefas."""
    lista_tarefas = sessao.exec(select(Tarefa).offset(0)).all()

    return lista_tarefas

# POST /tarefas: Cria tarefa
@APP.post("/tarefas", status_code=201)
async def post_tarefa(sessao: SESSAO, titulo: str, descricao: str = None):
    """Rota para criar uma tarefa."""
    tarefa_nova = Tarefa(
        titulo=titulo,
        descricao=descricao,
        data_criacao=datetime.now().astimezone(timezone.utc),
    )

    sessao.add(tarefa_nova)
    sessao.commit()
    sessao.refresh(tarefa_nova)

    return {"mensagem": "OK"}

# GET /tarefas/{id_tarefa}: Visualizar tarefa específica
@APP.get("/tarefas/{id_tarefa}")
async def tarefa_especifica(sessao: SESSAO, id_tarefa: int) -> Tarefa:
    """Rota para visualizar uma tarefa específica"""
    # select * from tarefas where id == id_tarefa
    regra = select(Tarefa).where(Tarefa.id == id_tarefa)
    resultado = sessao.exec(regra).all()

    if resultado:
        return resultado[0]

    return {"mensagem": "Tarefa não existe"}

# PUT /tarefas/{id}: Atualiza tarefa específica
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

    return {"mensagem": "Tarefa excluída com sucesso"}

@APP.get("/")
async def index():
    """Rota raíz."""
    return {"mensagem": "Olá, mundo!"}

# um dicionário no formato {"mensagem": SEU NOME COMPLETO}
@APP.get("/autor")
async def autor():
    """Rota para retornar o autor da aplicação"""
    return {"mensagem": "Gisele Ferreira da Silva"}
