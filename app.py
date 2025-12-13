from flask import Flask
from flasgger import Swagger
from payment_methods.Pix import Pix

app = Flask(__name__)
swagger = Swagger(app)

@app.route("/")
def hello_world():
    """
    A simple hello world endpoint.
    ---
    responses:
      200:
        description: A greeting message
        schema:
          type: object
          properties:
            message:
              type: string
              example: Hello, World!
    """
    pix_tst = Pix(
        merchant_name="Pedro Santana",
        pix_key="pedroems.147@gmail.com",
        amount=100.50,
        merchant_city="Salgueiro",
        transaction_id="txid_001"
    )
    payload = pix_tst.generate_payload()
    pix_tst.generate_qr_code("pix_qr.png")
    return {"message": "Hello, World!", "payload": payload}