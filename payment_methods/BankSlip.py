from utils.ensurepip import _ensure_pip
_ensure_pip()

import sys, subprocess
subprocess.run([sys.executable, "-m", "pip", "install", "python3-boleto"], check=True)

from pyboleto.bank.santander import BoletoSantander
from pyboleto.pdf import BoletoPDF
from datetime import datetime, timedelta

class BankSlip:
    def __init__(self,
                 payer_name: str,
                 payer_document: str,
                 amount: float,
                 payer_address: str,
                 payer_neighborhood: str,
                 payer_city: str,
                 payer_state: str,
                 payer_zip: str):
        self.payer_name = payer_name
        self.payer_document = payer_document
        self.amount = amount
        self.payer_address = payer_address
        self.payer_neighborhood = payer_neighborhood
        self.payer_city = payer_city
        self.payer_state = payer_state
        self.payer_zip = payer_zip
    
    def __generate_bank_slip(self) -> BoletoSantander:
        self.bank_slip = BoletoSantander()

        # Beneficiary
        self.bank_slip.cedente = "Bookify LTDA"
        self.bank_slip.cedente_documento = "12.345.678/0001-90"
        self.bank_slip.cedente_logradouro = "Av. José Caetano de Almeida, 1000"
        self.bank_slip.cedente_bairro = "Centro"
        self.bank_slip.cedente_cidade = "Quixadá"
        self.bank_slip.cedente_uf = "CE"
        self.bank_slip.cedente_cep = "63900-000"

        # Bank data
        self.bank_slip.agencia_cedente = "4300"  # ponto de venda
        self.bank_slip.conta_cedente = "9901760"  # últimos 7 dígitos
        self.bank_slip.carteira = "102"  # Santander: 101/102/201

        # Document
        self.bank_slip.numero_documento = "0001"
        self.bank_slip.nosso_numero = "000000000001"  # 12 dígitos para Santander
        self.bank_slip.valor_documento = self.amount
        self.bank_slip.data_documento = datetime.today().date() - timedelta(weeks=100)
        self.bank_slip.data_processamento = datetime.today().date() - timedelta(weeks=100)
        self.bank_slip.data_vencimento = (datetime.today() + timedelta(days=7)).date() - timedelta(weeks=100)

        # Payer
        self.bank_slip.sacado_nome = self.payer_name
        self.bank_slip.sacado_documento = self.payer_document
        self.bank_slip.sacado_endereco = self.payer_address
        self.bank_slip.sacado_bairro = self.payer_neighborhood
        self.bank_slip.sacado_cidade = self.payer_city
        self.bank_slip.sacado_uf = self.payer_state
        self.bank_slip.sacado_cep = self.payer_zip

        return self.bank_slip
    
    def generate_bank_slip_pdf(self, file_path: str) -> bytes:
        if not hasattr(self, 'bank_slip'):
            self.__generate_bank_slip()

        boleto_pdf = BoletoPDF(file_path)
        boleto_pdf.drawBoleto(self.bank_slip)
        boleto_pdf.save()

        with open(file_path, "rb") as pdf_file:
            return pdf_file.read()