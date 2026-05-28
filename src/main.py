from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, Field
from typing import List, Optional
from src.schemas.schemas import Cliente, Conta, Transacao
from src.models.models import (
    Cliente as ClienteModel,
    Conta as ContaModel,
    Transacao as TransacaoModel,
)
from src.services.auth import (
    criar_hash_senha,
    verificar_senha,
    criar_token_jwt,
    verificar_token_jwt,
)
from src.database import criar_banco
import aiosqlite

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")
BANCO_DADOS = "c:\\Users\\Bruno\\Documents\\Alura\\API_Bancaria\\banco.db"


class LoginRequest(BaseModel):
    cpf: str
    senha: str


@app.on_event("startup")
async def startup_event():
    await criar_banco()


async def usuario_autenticado(token: str = Depends(oauth2_scheme)):
    """Valida token JWT e retorna dados do usuário autenticado."""
    dados = verificar_token_jwt(token)
    if not dados:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
        )
    return dados


class Valor(BaseModel):
    valor: float = Field(..., gt=0)


class TransferenciaReq(BaseModel):
    destino: int
    valor: float = Field(..., gt=0)


@app.post("/clientes", response_model=Cliente)
async def cadastrar_cliente(cliente: Cliente):
    """Cadastra um novo cliente."""
    hash_senha = criar_hash_senha(cliente.senha)
    await ClienteModel.criar(
        cliente.nome,
        cliente.endereco,
        cliente.cpf,
        cliente.idade,
        cliente.genero,
        hash_senha,
    )
    async with aiosqlite.connect(BANCO_DADOS) as db:
        cursor = await db.execute(
            "SELECT * FROM clientes WHERE cpf = ?", (cliente.cpf,)
        )
        row = await cursor.fetchone()
        return Cliente(
            id=row[0],
            nome=row[1],
            endereco=row[2],
            cpf=row[3],
            idade=row[4],
            genero=row[5],
        )


@app.post("/login")
async def login(request: Request):
    """Realiza login e retorna o token JWT."""
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        payload = await request.json()
        cpf = payload.get("cpf")
        senha = payload.get("senha")
    else:
        form = await request.form()
        cpf = form.get("cpf") or form.get("username")
        senha = form.get("senha") or form.get("password")
    if not cpf or not senha:
        raise HTTPException(status_code=400, detail="CPF ou senha incorretos")
    cliente = await ClienteModel.buscar_por_cpf(cpf)
    if not cliente:
        raise HTTPException(status_code=400, detail="CPF ou senha incorretos")
    async with aiosqlite.connect(BANCO_DADOS) as db:
        cursor = await db.execute(
            "SELECT senha_hash FROM clientes WHERE cpf = ?", (cpf,)
        )
        row = await cursor.fetchone()
        if not row or not verificar_senha(senha, row[0]):
            raise HTTPException(status_code=400, detail="CPF ou senha incorretos")
    token = criar_token_jwt({"sub": cpf})
    return {"access_token": token, "token_type": "bearer"}


@app.post("/contas", response_model=Conta)
async def criar_conta(conta: Conta, usuario=Depends(usuario_autenticado)):
    """Cria uma nova conta para um cliente."""
    await ContaModel.criar(conta.agencia, conta.numero, conta.id_cliente, conta.tipo)
    async with aiosqlite.connect(BANCO_DADOS) as db:
        cursor = await db.execute(
            "SELECT * FROM contas WHERE numero = ? AND id_cliente = ?",
            (conta.numero, conta.id_cliente),
        )
        row = await cursor.fetchone()
        return Conta(
            id=row[0],
            agencia=row[1],
            numero=row[2],
            tipo=row[4],
            id_cliente=row[3],
            saldo=row[5],
            ativo=row[6],
        )


@app.get("/clientes/{id_cliente}/contas", response_model=List[Conta])
async def listar_contas(id_cliente: int, usuario=Depends(usuario_autenticado)):
    """Lista todas as contas de um cliente."""
    async with aiosqlite.connect(BANCO_DADOS) as db:
        cursor = await db.execute(
            "SELECT * FROM contas WHERE id_cliente = ?", (id_cliente,)
        )
        contas = await cursor.fetchall()
        return [
            Conta(
                id=row[0],
                agencia=row[1],
                numero=row[2],
                tipo=row[4],
                id_cliente=row[3],
                saldo=row[5],
                ativo=row[6],
            )
            for row in contas
        ]


@app.post("/contas/{id_conta}/deposito", response_model=Transacao)
async def realizar_deposito(
    id_conta: int, body: Valor, usuario=Depends(usuario_autenticado)
):
    """Realiza um depósito em uma conta."""
    valor = round(body.valor, 2)
    if valor <= 0:
        raise HTTPException(status_code=400, detail="Valor inválido para depósito.")
    conta = await ContaModel.buscar_por_id(id_conta)
    if not conta or not conta[6]:
        raise HTTPException(status_code=404, detail="Conta não encontrada ou inativa.")
    novo_saldo = round(conta[5] + valor, 2)
    async with aiosqlite.connect(BANCO_DADOS) as db:
        await db.execute(
            "UPDATE contas SET saldo = ? WHERE id = ?", (novo_saldo, id_conta)
        )
        await db.commit()
    await TransacaoModel.criar("entrada", valor, id_conta)
    async with aiosqlite.connect(BANCO_DADOS) as db:
        cursor = await db.execute(
            "SELECT * FROM transacoes WHERE id_conta = ? ORDER BY id DESC LIMIT 1",
            (id_conta,),
        )
        row = await cursor.fetchone()
        return Transacao(
            id=row[0],
            tipo=row[1],
            valor=row[2],
            id_conta=row[3],
            origem=row[4],
            destino=row[5],
            data=row[6],
        )


@app.post("/contas/{id_conta}/saque", response_model=Transacao)
async def realizar_saque(
    id_conta: int, body: Valor, usuario=Depends(usuario_autenticado)
):
    """Realiza um saque de uma conta."""
    valor = round(body.valor, 2)
    if valor <= 0:
        raise HTTPException(status_code=400, detail="Valor inválido para saque.")
    conta = await ContaModel.buscar_por_id(id_conta)
    if not conta or not conta[6]:
        raise HTTPException(status_code=404, detail="Conta não encontrada ou inativa.")
    if conta[5] < valor:
        raise HTTPException(status_code=400, detail="Saldo insuficiente.")
    novo_saldo = round(conta[5] - valor, 2)
    async with aiosqlite.connect(BANCO_DADOS) as db:
        await db.execute(
            "UPDATE contas SET saldo = ? WHERE id = ?", (novo_saldo, id_conta)
        )
        await db.commit()
    await TransacaoModel.criar("saida", valor, id_conta)
    async with aiosqlite.connect(BANCO_DADOS) as db:
        cursor = await db.execute(
            "SELECT * FROM transacoes WHERE id_conta = ? ORDER BY id DESC LIMIT 1",
            (id_conta,),
        )
        row = await cursor.fetchone()
        return Transacao(
            id=row[0],
            tipo=row[1],
            valor=row[2],
            id_conta=row[3],
            origem=row[4],
            destino=row[5],
            data=row[6],
        )


@app.post("/contas/{id_conta}/transferencia", response_model=List[Transacao])
async def realizar_transferencia(
    id_conta: int, req: TransferenciaReq, usuario=Depends(usuario_autenticado)
):
    """Realiza uma transferência entre contas."""
    valor = round(req.valor, 2)
    destino = req.destino
    if valor <= 0:
        raise HTTPException(
            status_code=400, detail="Valor inválido para transferência."
        )
    if id_conta == destino:
        raise HTTPException(
            status_code=400, detail="Conta de origem e destino não podem ser iguais."
        )
    conta_origem = await ContaModel.buscar_por_id(id_conta)
    conta_destino = await ContaModel.buscar_por_id(destino)
    if (
        not conta_origem
        or not conta_origem[6]
        or not conta_destino
        or not conta_destino[6]
    ):
        raise HTTPException(
            status_code=404,
            detail="Conta de origem ou destino não encontrada ou inativa.",
        )
    if conta_origem[5] < valor:
        raise HTTPException(status_code=400, detail="Saldo insuficiente.")
    novo_saldo_origem = round(conta_origem[5] - valor, 2)
    novo_saldo_destino = round(conta_destino[5] + valor, 2)
    async with aiosqlite.connect(BANCO_DADOS) as db:
        await db.execute(
            "UPDATE contas SET saldo = ? WHERE id = ?", (novo_saldo_origem, id_conta)
        )
        await db.execute(
            "UPDATE contas SET saldo = ? WHERE id = ?", (novo_saldo_destino, destino)
        )
        await db.commit()
    await TransacaoModel.criar(
        "saida", valor, id_conta, origem=id_conta, destino=destino
    )
    await TransacaoModel.criar(
        "entrada", valor, destino, origem=id_conta, destino=destino
    )
    async with aiosqlite.connect(BANCO_DADOS) as db:
        cursor = await db.execute(
            "SELECT * FROM transacoes WHERE (id_conta = ? OR id_conta = ?) ORDER BY id DESC LIMIT 2",
            (id_conta, destino),
        )
        rows = await cursor.fetchall()
        return [
            Transacao(
                id=row[0],
                tipo=row[1],
                valor=row[2],
                id_conta=row[3],
                origem=row[4],
                destino=row[5],
                data=row[6],
            )
            for row in rows
        ]


@app.get("/contas/{id_conta}/extrato", response_model=List[Transacao])
async def extrato(id_conta: int, usuario=Depends(usuario_autenticado)):
    """Exibe o extrato de uma conta."""
    async with aiosqlite.connect(BANCO_DADOS) as db:
        cursor = await db.execute(
            "SELECT * FROM transacoes WHERE id_conta = ? ORDER BY data DESC",
            (id_conta,),
        )
        transacoes = await cursor.fetchall()
        return [
            Transacao(
                id=row[0],
                tipo=row[1],
                valor=row[2],
                id_conta=row[3],
                origem=row[4],
                destino=row[5],
                data=row[6],
            )
            for row in transacoes
        ]
