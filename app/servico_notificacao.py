"""Aplicação de notificações"""

from fastapi import FastAPI

NOTIFICACAO = FastAPI()


@NOTIFICACAO.post("/notificar")
async def notificar(id_tarefa: int, titulo: str):
    """Envia uma notificação referente à tarefa."""
    print(f"Tarefa '{titulo}' (id={id_tarefa}) finalizada!")
    return {"mensagem": "OK"}
