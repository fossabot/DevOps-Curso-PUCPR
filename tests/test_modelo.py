"""Testes unitários do modelo.py"""
from datetime import datetime
from app.modelo import Tarefa

def criar_tarefa_mock():
    """Função para retornar uma versão teste da classe Tarefa"""
    return Tarefa(
        _id=0,
        titulo="Tarefa teste",
        data_criacao=datetime.now().isoformat(timespec="seconds"),
    )

def test_nova_tarefa():
    """Função de teste para criar uma nova tarefa conforme a classe Tarefa"""
    t = criar_tarefa_mock()

    assert t.get_id() == 0
    assert t.titulo == "Tarefa teste"
    assert t.descricao is None
    assert t.data_criacao.isoformat() == datetime.now().isoformat(timespec="seconds")
    assert t.data_conclusao is None
    assert t.concluida is False

def test_tarefa_concluida():
    """Função para conclusão da tarefa criada"""
    t = criar_tarefa_mock()

    t.finalizar()
    assert t.concluida is True
    assert t.data_conclusao == datetime.now().isoformat(timespec="seconds")
