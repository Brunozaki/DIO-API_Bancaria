# API Bancária Assíncrona

Este projeto implementa uma API bancária simples, assíncrona, utilizando FastAPI, SQLite e autenticação JWT.

## Instalação

1. Clone o repositório e acesse a pasta do projeto.
2. Instale as dependências:

```bash
pip install fastapi[all] aiosqlite python-jose[cryptography] passlib
```

3. Execute o script de criação do banco de dados (opcional, será criado automaticamente ao rodar a API):

```bash
python src/database.py
```

4. Inicie a API:

```bash
uvicorn src.main:app --reload
```

## Endpoints Principais

- Cadastro de cliente
- Autenticação (JWT)
- Cadastro de conta
- Depósito
- Saque
- Transferência entre contas
- Extrato de conta

## Configuração no Insomnia

1. Abra o Insomnia e crie um novo workspace ou use um existente.
2. Crie um ambiente chamado `Desenvolvimento`.
3. Adicione as variáveis de ambiente abaixo:

```json
{
  "base_url": "http://127.0.0.1:8000",
  "token": ""
}
```

4. Crie requests usando `{{ base_url }}` no lugar do endereço fixo.
5. Para requests autenticados, adicione no header:

```
Authorization: Bearer {{ token }}
```

6. Execute o servidor local antes de testar: `uvicorn src.main:app --reload`.

## Exemplos de Requisições (Insomnia)

### Cadastro de Cliente
```
POST {{ base_url }}/clientes
{
  "nome": "João Silva",
  "endereco": "Rua A, 123",
  "cpf": "12345678900",
  "idade": 30,
  "genero": "M"
}
```

### Autenticação
```json
POST {{ base_url }}/login
{
  "cpf": "12345678900",
  "senha": "senha123"
}
```

Para o cliente de teste `Maria Souza` use:
```json
{
  "cpf": "98765432100",
  "senha": "senha456"
}
```

Se estiver usando o Swagger UI, envie os campos do formulário como `username` e `password`.

Após o login, copie o valor de `access_token` para a variável `token` do ambiente.

### Depósito
```
POST {{ base_url }}/contas/{id_conta}/deposito
{
  "valor": 100.00
}
```

### Saque
```
POST {{ base_url }}/contas/{id_conta}/saque
{
  "valor": 50.00
}
```

### Transferência
```
POST {{ base_url }}/contas/{id_conta}/transferencia
{
  "destino": 2,
  "valor": 25.00
}
```

### Extrato
```
GET {{ base_url }}/contas/{id_conta}/extrato
```

**Todos os endpoints (exceto cadastro e login) exigem autenticação JWT no header:**

```
Authorization: Bearer {{ token }}
```

---

Dúvidas? Abra uma issue ou entre em contato.
