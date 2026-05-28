import aiosqlite
from src.services.auth import criar_hash_senha

BANCO_DADOS = "c:\\Users\\Bruno\\Documents\\Alura\\API_Bancaria\\banco.db"


async def criar_banco():
    """Cria as tabelas do banco de dados e insere clientes e contas iniciais."""
    hash_joao = criar_hash_senha("senha123")
    hash_maria = criar_hash_senha("senha456")
    async with aiosqlite.connect(BANCO_DADOS) as db:
        await db.executescript("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            endereco TEXT NOT NULL,
            cpf TEXT UNIQUE NOT NULL,
            senha_hash TEXT NOT NULL,
            idade INTEGER NOT NULL,
            genero TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS contas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agencia TEXT NOT NULL,
            numero TEXT NOT NULL,
            id_cliente INTEGER NOT NULL,
            tipo TEXT NOT NULL,
            saldo REAL NOT NULL DEFAULT 0.00,
            ativo INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY (id_cliente) REFERENCES clientes(id)
        );
        CREATE TABLE IF NOT EXISTS transacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT NOT NULL,
            valor REAL NOT NULL,
            id_conta INTEGER NOT NULL,
            origem INTEGER,
            destino INTEGER,
            data TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_conta) REFERENCES contas(id)
        );
        """)
        await db.execute(
            "INSERT OR IGNORE INTO clientes (id, nome, endereco, cpf, senha_hash, idade, genero) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (1, "João Silva", "Rua A, 123", "12345678900", hash_joao, 30, "M"),
        )
        await db.execute(
            "INSERT OR IGNORE INTO clientes (id, nome, endereco, cpf, senha_hash, idade, genero) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (2, "Maria Souza", "Rua B, 456", "98765432100", hash_maria, 28, "F"),
        )
        await db.execute(
            "UPDATE clientes SET senha_hash = ? WHERE id = ? AND senha_hash IS NULL",
            (hash_joao, 1),
        )
        await db.execute(
            "UPDATE clientes SET senha_hash = ? WHERE id = ? AND senha_hash IS NULL",
            (hash_maria, 2),
        )
        await db.execute(
            "INSERT OR IGNORE INTO contas (id, agencia, numero, id_cliente, tipo, saldo, ativo) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (1, "0001", "12345-6", 1, "corrente", 1000.00, 1),
        )
        await db.execute(
            "INSERT OR IGNORE INTO contas (id, agencia, numero, id_cliente, tipo, saldo, ativo) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (2, "0001", "65432-1", 2, "poupanca", 500.00, 1),
        )
        await db.commit()


if __name__ == "__main__":
    import asyncio

    asyncio.run(criar_banco())
