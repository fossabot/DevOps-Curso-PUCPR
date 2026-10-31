"""Testes unitários da API"""
from datetime import datetime
from fastapi.testclient import TestClient
from app.api import APP

CLIENT = TestClient(APP)
DATAS = {
    "criacao": None,
    "conclusao": None
}

def test_index():
    """Função para testar a rota index"""
    resposta = CLIENT.get("/")
    assert resposta.status_code == 200
    assert resposta.json() == {"mensagem": "Olá, mundo!"}


# 1. Implementar um teste unitário para a rota /tarefas (GET)
def test_tarefas_get():
    """Função para teste da rota de tarefas"""
    resposta = CLIENT.get("/tarefas")
    assert resposta.status_code == 200

    # Testando se a rota retorna uma lista vazia
    assert resposta.json() == []


# 2. Implementar um teste unitário para a rota /tarefas (POST)
def test_tarefas_post():
    """Função para teste de POST da rota tarefas"""
    resposta = CLIENT.post("/tarefas?titulo=teste&descricao=teste")
    DATAS["criacao"] = datetime.now().isoformat(timespec="seconds")

    assert resposta.status_code == 201
    assert resposta.json() == {"mensagem": "OK"}

    resposta = CLIENT.get("/tarefas")
    assert resposta.json() == [{"0": "teste"}]

def test_tarefa_criada():
    """Função para teste da criação de tarefas"""
    resposta = CLIENT.get("/tarefas/0")
    assert resposta.status_code == 200
    assert resposta.json() == {
        "_id": 0,
        "titulo": "teste",
        "descricao": "teste",
        "concluida": False,
        "data_criacao": str(DATAS["criacao"]),
        "data_conclusao": None,
    }


# 3. Implementar um teste unitário para a rota /tarefas/{id} (PUT)
def test_tarefas_put():
    """Função para teste da atualização de tarefas"""
    resposta = CLIENT.put("/tarefas/0")
    DATAS["conclusao"] = datetime.now().isoformat(timespec="seconds")

    assert resposta.json() == {"mensagem": "Tarefa atualizada"}

    resposta = CLIENT.put("/tarefas/1")
    assert resposta.json() == {"mensagem": "Tarefa não existe"}


# 4. Implementar um teste unitário para a rota /tarefas/{id} (GET)
def test_tarefas_get_id():
    """Função para teste de consulta das tarefas"""
    resposta = CLIENT.get("/tarefas/0")
    assert resposta.status_code == 200
    assert resposta.json() == {
        "_id": 0,
        "titulo": "teste",
        "descricao": "teste",
        "concluida": True,
        "data_criacao": str(DATAS["criacao"]),
        "data_conclusao": str(DATAS["conclusao"]),
    }

    resposta = CLIENT.get("/tarefas/1")
    assert resposta.json() == {"mensagem": "Tarefa não existe"}


# 5. Implementar um teste unitário para a rota /tarefas/{id} (DELETE)
def test_tarefas_delete():
    """Função para teste de exclusão de tarefas"""
    resposta = CLIENT.delete("/tarefas/1")
    assert resposta.json() == {"mensagem": "Tarefa não existe"}

    resposta = CLIENT.delete("/tarefas/0")
    assert resposta.json() == {"mensagem": "Tarefa apagada"}

    resposta = CLIENT.get("/tarefas")
    assert resposta.json() == []


def test_autor():
    """Função para validação da rota autor"""
    resposta = CLIENT.get("/autor")

    assert resposta.status_code == 200
    assert resposta.json() == {"mensagem": "Gisele Ferreira da Silva"}
