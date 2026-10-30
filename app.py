from fastapi import FastAPI
from datetime import datetime
import requests

APP = FastAPI()
TAREFAS = []

# Estrutura da tarefa
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
    lista_somente_id_titulo = []

    for tarefa in TAREFAS:
        id_tarefa = tarefa['id']
        titulo_tarefa = tarefa['titulo']

        lista_somente_id_titulo.append({id_tarefa: titulo_tarefa})

    return lista_somente_id_titulo

# POST /tarefas: Cria tarefa
@APP.post("/tarefas", status_code=201)
async def post_tarefa(titulo: str, descricao: str):
    global TAREFAS

    tarefa_nova = criar_tarefa(titulo, descricao)

    TAREFAS.append(tarefa_nova)

    return {"mensagem": "OK"}

# GET /tarefas/{id}: Visualizar tarefa específica
@APP.get("/tarefas/{id}")
async def tarefa_especifica(id: int):
    for tarefa in TAREFAS:
        if id == int(tarefa["id"]):
            return tarefa

    return {"mensagem": "Tarefa não existe"}

# PUT /tarefas/{id}: Atualiza tarefa específica
@APP.put("/tarefas/{id}")
async def concluir_tarefa(id: int):
    for tarefa in TAREFAS:
        if id == int(tarefa['id']) and tarefa['concluida'] == False:
            tarefa['concluida'] = True
            tarefa['concluida_em'] = datetime.now().isoformat(timespec='seconds')
            titulo = tarefa['titulo']

            try:
                resp = requests.post(
                    f"http://localhost:8000/notificar?id={id}&titulo={titulo}",
                    timeout=1
                )
            except Exception as e:
                print(e)
                
            return {"mensagem": "Tarefa atualizada"}
    
    return {"mensagem": "Tarefa não existe"}

# DELETE /tarefas/{id}: Exclui tarefa
@APP.delete("/tarefas/{id}")
async def apagar_tarefa(id: int):
    global TAREFAS

    indice = 0
    for tarefa in TAREFAS:
        if id == int(tarefa['id']):
            TAREFAS.pop(indice)
            return {"mensagem": "Tarefa apagada"}

        indice += 1
    
    return {"mensagem": "Tarefa não existe"}

@APP.get("/")
async def index():
    return {"mensagem": "Olá, mundo!"}