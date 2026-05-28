from pydantic import BaseModel, Field
from typing import Optional


class Cliente(BaseModel):
    id: Optional[int] = None
    nome: str
    endereco: str
    cpf: str
    idade: int
    genero: str
    senha: Optional[str] = None


class Conta(BaseModel):
    id: Optional[int] = None
    agencia: str
    numero: str
    tipo: str
    id_cliente: int
    saldo: Optional[float] = None
    ativo: Optional[int] = None


class Transacao(BaseModel):
    id: Optional[int] = None
    tipo: str
    valor: float = Field(..., gt=0)
    id_conta: int
    origem: Optional[int] = None
    destino: Optional[int] = None
    data: Optional[str] = None
