# API Bancária

Este projeto é uma API simples de banco que permite cadastrar clientes, criar contas e movimentar dinheiro.

A aplicação roda localmente e usa:
- FastAPI para a interface de API,
- SQLite para guardar dados,
- JWT para proteger endpoints que precisam de login.

O projeto inclui rotas para:
- criar clientes,
- fazer login,
- cadastrar contas,
- depósito,
- saque,
- transferência entre contas,
- verificar o extrato.

A ideia é ter uma API leve para testar operações bancárias básicas, sem aprofundar em detalhes técnicos.
