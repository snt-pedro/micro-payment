# Micro Payment Service

Implementação de um microsserviço de pagamentos utilizando Flask.

## Funcionalidades
- Suporte a geração de cobranças via Pix e Boleto Bancário.
- Integração com Redis para armazenamento temporário do status dos pagamentos.
- Mecanismos de resiliência, incluindo retry e circuit breaker.

## Requisitos
- Python 3.7 ou superior
- Redis Server
- Bibliotecas Python listadas em `pyproject.toml`

## Como Executar

1. Inicie o servidor Redis localmente (configure a porta no arquivo `.env`).
2. Inicie o ambiente virtual e instale as dependências:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   .venv\Scripts\activate     # Windows
   uv sync
   ```
3. Execute o aplicativo Flask:
   ```bash
   python run.py
   ```