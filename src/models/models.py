import aiosqlite

BANCO_DADOS = "c:\\Users\\Bruno\\Documents\\Alura\\API_Bancaria\\banco.db"


class Cliente:
    """Classe para operações com clientes."""

    @staticmethod
    async def buscar_por_cpf(cpf: str):
        async with aiosqlite.connect(BANCO_DADOS) as db:
            cursor = await db.execute("SELECT * FROM clientes WHERE cpf = ?", (cpf,))
            return await cursor.fetchone()

    @staticmethod
    async def criar(
        nome: str, endereco: str, cpf: str, idade: int, genero: str, senha_hash: str
    ):
        async with aiosqlite.connect(BANCO_DADOS) as db:
            await db.execute(
                "INSERT INTO clientes (nome, endereco, cpf, senha_hash, idade, genero) VALUES (?, ?, ?, ?, ?, ?)",
                (nome, endereco, cpf, senha_hash, idade, genero),
            )
            await db.commit()


class Conta:
    """Classe para operações com contas."""

    @staticmethod
    async def criar(
        agencia: str,
        numero: str,
        id_cliente: int,
        tipo: str,
        saldo: float = 0.0,
        ativo: int = 1,
    ):
        async with aiosqlite.connect(BANCO_DADOS) as db:
            await db.execute(
                "INSERT INTO contas (agencia, numero, id_cliente, tipo, saldo, ativo) VALUES (?, ?, ?, ?, ?, ?)",
                (agencia, numero, id_cliente, tipo, saldo, ativo),
            )
            await db.commit()

    @staticmethod
    async def buscar_por_id(id_conta: int):
        async with aiosqlite.connect(BANCO_DADOS) as db:
            cursor = await db.execute("SELECT * FROM contas WHERE id = ?", (id_conta,))
            return await cursor.fetchone()


class Transacao:
    """Classe para operações com transações."""

    @staticmethod
    async def criar(
        tipo: str, valor: float, id_conta: int, origem: int = None, destino: int = None
    ):
        async with aiosqlite.connect(BANCO_DADOS) as db:
            await db.execute(
                "INSERT INTO transacoes (tipo, valor, id_conta, origem, destino) VALUES (?, ?, ?, ?, ?)",
                (tipo, valor, id_conta, origem, destino),
            )
            await db.commit()
