""" API para gerenciamento de tarefas. Permite criar, consultar, atualizar e excluir tarefas."""

from datetime import datetime
from fastapi import FastAPI
import requests
from requests.exceptions import ConnectionError as RequestConnectionError

APP = FastAPI()
TAREFAS = []

# Estrutura da tarefa criada
""" 
{
    "id" -> int,
    "titulo" -> str,
    "descricao" -> str,
    "concluida" -> bool,
    "criada_em" -> datetime
}
"""
def criar_tarefa(titulo, descricao):
    """ Função para criar uma tarefa e retornar um dicionário """
    return {
        "id": len(TAREFAS),
        "titulo": titulo,
        "descricao": descricao,
        "concluida": False,
        "criada_em": datetime.now().isoformat(timespec="seconds")
    }

# GET /tarefas: Lista todas as tarefas (somente id e titulo)
@APP.get("/tarefas")
async def tarefas():
    """Rota para listagem das tarefas"""
    lista_somente_id_titulo = []

    for tarefa in TAREFAS:
        id_tarefa = tarefa['id_tarefa']
        titulo_tarefa = tarefa['titulo']

        lista_somente_id_titulo.append({id_tarefa: titulo_tarefa})

    return lista_somente_id_titulo

# POST /tarefas: Cria tarefa
@APP.post("/tarefas", status_code=201)
async def post_tarefa(titulo: str, descricao: str):
    """Rota para criação de tarefas"""
    tarefa_nova = criar_tarefa(titulo, descricao)

    TAREFAS.append(tarefa_nova)

    return {"mensagem": "OK"}

# GET /tarefas/{id}: Visualizar tarefa específica
@APP.get("/tarefas/{id}")
async def tarefa_especifica(id_tarefa: int):
    """Rota para a visualização de tarefas específicas"""
    for tarefa in TAREFAS:
        if id_tarefa == int(tarefa["id"]):
            return tarefa

    return {"mensagem": "Tarefa não existe"}

# PUT /tarefas/{id}: Atualiza tarefa específica
@APP.put("/tarefas/{id_tarefa}")
async def concluir_tarefa(id_tarefa: int):
    """Rota para atualização de tarefas específicas"""
    for tarefa in TAREFAS:
        if id_tarefa == int(tarefa['id']) and tarefa['concluida'] is False:
            tarefa['concluida'] = True
            tarefa['concluida_em'] = datetime.now().isoformat(timespec='seconds')
            titulo = tarefa['titulo']

            try:
                _ = requests.post(
                    f"http://localhost:8000/notificar?id={id}&titulo={titulo}",
                    timeout=1
                )
            except RequestConnectionError as e:
                print(e)
            return {"mensagem": "Tarefa atualizada"}

    return {"mensagem": "Tarefa não existe"}
# DELETE /tarefas/{id}: Exclui tarefa
@APP.delete("/tarefas/{id}")
async def apagar_tarefa(id_tarefa: int):
    """ Rota para deletar tarefas """
    indice = 0
    for tarefa in TAREFAS:
        if id_tarefa == int(tarefa['id']):
            TAREFAS.pop(indice)
            return {"mensagem": "Tarefa apagada"}

        indice += 1
    return {"mensagem": "Tarefa não existe"}
@APP.get("/")
async def index():
    """Rota padrão index"""
    return {"mensagem": "Olá, mundo!"}
