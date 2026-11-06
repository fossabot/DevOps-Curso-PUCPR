
"""Testes unitários para a execução das tarefas."""

from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine

from app.api import APP, criar_sessao


BANCO = create_engine(
    "sqlite:///banco.db",
    connect_args={"check_same_thread": False}
)


@pytest.fixture(name="sessao")
def fixture_sessao():
    """Configura a sessão de testes com banco"""

    SQLModel.metadata.create_all(BANCO)

    with Session(BANCO) as sessao:
        yield sessao

    SQLModel.metadata.drop_all(BANCO)


@pytest.fixture(name="cliente")
def fixture_cliente(sessao: Session):
    """Configura o cliente de testes da API."""

    def get_sessao():
        return sessao

    APP.dependency_overrides[criar_sessao] = get_sessao

    cliente = TestClient(APP)
    yield cliente

    APP.dependency_overrides.clear()


def test_index(cliente: TestClient):
    """Testa a rota inicial da aplicação."""

    resposta = cliente.get("/")

    assert resposta.status_code == 200
    assert resposta.json() == {"mensagem": "Olá, mundo!"}


def test_tarefas_get(cliente: TestClient):
    """Testa se a rota GET retorna uma lista vazia."""

    resposta = cliente.get("/tarefas")

    assert resposta.status_code == 200
    assert resposta.json() == []


def test_tarefas_post(cliente: TestClient):
    """Testa a criação de uma nova tarefa."""

    inicio = datetime.now(timezone.utc).replace(microsecond=0)

    resposta = cliente.post("/tarefas?titulo=teste&descricao=teste")

    fim = datetime.now(timezone.utc).replace(microsecond=0)

    assert resposta.status_code == 201
    assert resposta.json() == {"mensagem": "OK"}

    resposta = cliente.get("/tarefas")

    dados = resposta.json()[0]

    assert dados["_id"] == 1
    assert dados["descricao"] == "teste"
    assert dados["concluida"] is False
    assert dados["titulo"] == "teste"
    assert dados["data_conclusao"] is None

    data_criacao = datetime.fromisoformat(
        dados["data_criacao"].replace("Z", "+00:00")
    )

    assert inicio <= data_criacao <= fim


def test_tarefas_put(cliente: TestClient):
    """Testa a atualização e conclusão de uma tarefa."""

    resposta = cliente.post("/tarefas?titulo=teste&descricao=teste")

    resposta = cliente.put("/tarefas/1")

    assert resposta.json() == {"mensagem": "Tarefa atualizada"}

    resposta = cliente.put("/tarefas/0")

    assert resposta.json() == {"mensagem": "Tarefa não existe"}

    resposta = cliente.get("/tarefas/1")

    assert resposta.status_code == 200

    dados = resposta.json()

    assert dados["_id"] == 1
    assert dados["descricao"] == "teste"
    assert dados["concluida"] is True
    assert dados["titulo"] == "teste"
    assert dados["data_conclusao"] is not None


def test_tarefas_delete(cliente: TestClient):
    """Testa a exclusão de uma tarefa."""

    resposta = cliente.post("/tarefas?titulo=teste&descricao=teste")

    resposta = cliente.delete("/tarefas/0")

    assert resposta.json() == {"mensagem": "Tarefa não existe"}

    resposta = cliente.delete("/tarefas/1")

    assert resposta.json() == {"mensagem": "Tarefa removida"}

    resposta = cliente.get("/tarefas")

    assert resposta.json() == []


def test_autor(cliente: TestClient):
    """Testa a rota que retorna o autor da aplicação."""

    resposta = cliente.get("/autor")

    assert resposta.status_code == 200
    assert resposta.json() == {
        "mensagem": "Gisele Ferreira da Silva"
    }
