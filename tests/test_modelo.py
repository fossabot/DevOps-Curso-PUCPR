"""Teste unitário para a classe Tarefa"""
from datetime import datetime, timezone
from app.modelo import Tarefa


def criar_tarefa_mock():
    """Cria uma tarefa mock para teste"""
    return Tarefa(
        titulo="Tarefa teste",
        data_criacao=datetime.now().replace(microsecond=0),
    )


def test_nova_tarefa():
    """Teste unitário para criar uma nova tarefa"""
    t = criar_tarefa_mock()

    assert t.get_id() == None
    assert t.titulo == "Tarefa teste"
    assert t.descricao == None
    assert t.data_criacao == datetime.now().replace(microsecond=0)
    assert t.data_conclusao == None
    assert t.concluida == False

def test_tarefa_concluida():
    """Teste unitário para concluir uma tarefa"""
    t = criar_tarefa_mock()

    t.finalizar()
    assert t.concluida == True
    assert t.data_conclusao == datetime.now().astimezone(timezone.utc).replace(microsecond=0)
