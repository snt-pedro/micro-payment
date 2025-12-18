import base64
import json
from flask import Flask, request
from flasgger import Swagger, swag_from
from payment_methods.Pix import Pix
from payment_methods.BankSlip import BankSlip
from utils.redis_client import redis_client
from decorators.circuit_breaker import circuit_breaker_decorator
from decorators.retry import retry_decorator

app = Flask(__name__)
swagger = Swagger(app)

@app.route("/generate_pix", methods=["POST"])
@swag_from(
    {
        "tags": ["Payment"],
        "summary": "Gera um pagamento PIX",
        "description": "Esse endpoint cria um novo registro de pagamento PIX.",
        "parameters": [
            {
                "name": "body",
                "in": "body",
                "required": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "merchant_name": {"type": "string", "example": "Pedro Santana"},
                        "pix_key": {"type": "string", "example": "pedroems.147@gmail.com"},
                        "amount": {"type": "number", "format": "float", "example": 10.50},
                        "merchant_city": {"type": "string", "example": "Salgueiro"},
                        "transaction_id": {"type": "string", "example": "txid001"}
                    }
                }
            }
        ],
        "responses": {
            200: {
                "description": "Pagamento registrado com sucesso",
                "examples": {
                    "application/json": {
                        "message": "Pagamento registrado com sucesso!",
                        "transaction_id": "txid001",
                        "amount": 10.50,
                        "merchant_name": "Pedro Santana",
                        "merchant_city": "Salgueiro",
                    }
                },
            },
            400: {
                "description": "Requisição inválida",
                "examples": {
                    "application/json": {
                        "message": "Invalid request",
                        "details": "Missing required fields.",
                    }
                },
            },
            500: {
                "description": "Erro interno do servidor",
                "examples": {
                    "application/json": {
                        "message": "Internal Server Error",
                        "details": "Falha no processamento do pagamento.",
                    }
                },
            },
        },
    }
)
@circuit_breaker_decorator
def generate_pix():
    json_data = request.get_json()

    if json_data.get("fail", False):
        raise Exception("Simulated failure for resilience testing.")
    
    merchant_name = json_data.get("merchant_name")
    pix_key = json_data.get("pix_key")
    amount = json_data.get("amount")
    merchant_city = json_data.get("merchant_city")
    transaction_id = json_data.get("transaction_id")

    if not all([merchant_name, pix_key, amount, merchant_city, transaction_id]):
        return {"message": "Missing required headers"}, 400
    
    pix_payment = Pix(
        merchant_name=merchant_name,
        pix_key=pix_key,
        amount=float(amount),
        merchant_city=merchant_city,
        transaction_id=transaction_id
    )

    qrcode_bytes = pix_payment.generate_qr_code("pix_qr.png")
    qrcode_b64 = base64.b64encode(qrcode_bytes).decode("utf-8")

    redis_client.set(qrcode_b64, json.dumps({"status": "registered"}))

    return {
        "message": "Pagamento registrado com sucesso!",
        "merchant_name": merchant_name,
        "amount": amount,
        "qrcode_base64": qrcode_b64,
        "qrcode_mime": "image/png"
    }, 200


@app.route("/generate_bankslip", methods=["POST"])
@swag_from(
    {
        "tags": ["Payment"],
        "summary": "Gera um boleto bancário",
        "description": "Esse endpoint gera um boleto bancário para pagamento.",
        "parameters": [
            {
                "name": "body",
                "in": "body",
                "required": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "payer_name": {"type": "string", "example": "Victor Pinheiro"},
                        "payer_document": {"type": "string", "example": "123.456.789-00"},
                        "amount": {"type": "number", "format": "float", "example": 150.75},
                        "payer_address": {"type": "string", "example": "Av. José Caetano de Almeida, 123"},
                        "payer_neighborhood": {"type": "string", "example": "Combate"},
                        "payer_city": {"type": "string", "example": "Ceará"},
                        "payer_state": {"type": "string", "example": "CE"},
                        "payer_zip": {"type": "string", "example": "63900-000"}
                    }
                }
            }
        ],
        "responses": {
            200: {
                "description": "Boleto gerado com sucesso",
                "examples": {
                    "application/json": {
                        "message": "Boleto gerado com sucesso!",
                        "payer_name": "João Silva",
                        "amount": 150.75,
                        "bank_slip": "<bank slip details>"
                    }
                },
            },
            400: {
                "description": "Requisição inválida",
                "examples": {
                    "application/json": {
                        "message": "Missing required fields"
                    }
                },
            },
        },
    }
)
@circuit_breaker_decorator
def generate_bankslip():
    json_data = request.get_json()

    if json_data.get("fail", False):
        raise Exception("Simulated failure for resilience testing.")

    payer_name = json_data.get("payer_name")
    payer_document = json_data.get("payer_document")
    amount = json_data.get("amount")
    payer_address = json_data.get("payer_address")
    payer_neighborhood = json_data.get("payer_neighborhood")
    payer_city = json_data.get("payer_city")
    payer_state = json_data.get("payer_state")
    payer_zip = json_data.get("payer_zip")

    if not all([payer_name, payer_document, amount, payer_address, payer_neighborhood, payer_city, payer_state, payer_zip]):
        return {"message": "Missing required fields"}, 400
    
    bank_slip_payment = BankSlip(
        payer_name=payer_name,
        payer_document=payer_document,
        amount=float(amount),
        payer_address=payer_address,
        payer_neighborhood=payer_neighborhood,
        payer_city=payer_city,
        payer_state=payer_state,
        payer_zip=payer_zip
    )
    bank_slip_bytes = bank_slip_payment.generate_bank_slip_pdf("bank_slip.pdf")
    bank_slip_b64 = base64.b64encode(bank_slip_bytes).decode("utf-8")

    redis_client.set(bank_slip_b64, json.dumps({"status": "registered"}))

    return {
        "message": "Bank slip generated successfully!",
        "payer_name": payer_name,
        "amount": amount,
        "bank_slip": bank_slip_b64,
        "bank_slip_mime": "application/pdf"
    }, 200


@app.route("/payment_status", methods=["POST"])
@swag_from(
    {
        "tags": ["Payment"],
        "summary": "Verifica o status de um pagamento",
        "description": "Esse endpoint verifica o status de um pagamento.",
        "parameters": [
            {
                "name": "body",
                "in": "body",
                "required": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "transaction_id": {"type": "string", "example": "1234567890"}
                    }
                }
            }
        ],
        "responses": {
            200: {
                "description": "Status do pagamento recuperado com sucesso",
                "examples": {
                    "application/json": {
                        "message": "Payment status retrieved successfully!",
                        "transaction_id": "1234567890",
                        "status": "paid"
                    }
                },
            },
            404: {
                "description": "Pagamento não encontrado",
                "examples": {
                    "application/json": {
                        "message": "Payment not found"
                    }
                },
            },
        },
    }
)
@retry_decorator(max_retries=5, delay=2)
def payment_status():
    json_data = request.get_json()
    transaction_id = json_data.get("transaction_id")

    if not transaction_id:
        return {"message": "Missing required fields"}, 400

    payment_data = redis_client.get(transaction_id)

    if not payment_data:
        return {"message": "Payment not found"}, 404
        
    return {
        "message": "Payment status retrieved successfully!",
        "payment_status": json.loads(payment_data).get("status"),
        "transaction_id": transaction_id
    }, 200