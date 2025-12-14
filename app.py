from flask import Flask, request
from flasgger import Swagger, swag_from
from payment_methods.Pix import Pix
import base64

app = Flask(__name__)
swagger = Swagger(app)

@app.route("/", methods=["POST"])
@swag_from(
    {
        "tags": ["Payment"],
        "summary": "Registra um novo pagamento",
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
def hello_world():
    json_data = request.get_json()

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
    payload = pix_payment.generate_payload()

    qr_path = "pix_qr.png"
    pix_payment.generate_qr_code(qr_path)

    try:
        with open(qr_path, "rb") as f:
            qrcode_b64 = base64.b64encode(f.read()).decode("utf-8")
    except Exception as e:
        return {"message": "Falha ao gerar a imagem do QRCode", "error": str(e)}, 500

    return {
        "message": "Pagamento registrado com sucesso!",
        "merchant_name": merchant_name,
        "amount": amount,
        "payload": payload,
        "qrcode_base64": qrcode_b64,
        "qrcode_mime": "image/png"
    }, 200