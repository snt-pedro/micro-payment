import re
import qrcode
import crcmod
import unicodedata

class Pix:
    def _fmt_struct(self, id: int, value: str) -> str:
        return f"{id:02}{len(value):02}{value}"
    
    def _fmt_str(self, text: str) -> str:
        text = unicodedata.normalize('NFKD', text)
        text = text.encode('ascii', 'ignore').decode('ascii')
        text = re.sub(r'[^A-Z0-9]', '', text.upper())
        return text

    def __init__(self,
                 merchant_name: str,
                 pix_key: str,
                 amount: float,
                 merchant_city: str,
                 transaction_id: str):

        self.merchant_name = self._fmt_str(merchant_name)[:20]
        self.pix_key = pix_key.strip().lower()
        self.amount = amount
        self.merchant_city = self._fmt_str(merchant_city)[:15]
        self.transaction_id = self._fmt_str(transaction_id)[:25]

        self.payload_format = self._fmt_struct(0, '01')

        self.merchant_acc_info_gui = self._fmt_struct(0, 'br.gov.bcb.pix')
        self.merchant_acc_info_key = self._fmt_struct(1, self.pix_key)
        self.merchant_acc_info_value = self.merchant_acc_info_gui + self.merchant_acc_info_key
        self.merchant_acc_info = self._fmt_struct(26, self.merchant_acc_info_value)

        self.merchant_category_code = self._fmt_struct(52, '0000')
        self.transaction_currency = self._fmt_struct(53, '986') # BRL
        self.transaction_amount = self._fmt_struct(54, f"{self.amount:.2f}")
        self.country_code = self._fmt_struct(58, 'BR')
        self.merchant_name = self._fmt_struct(59, self.merchant_name)
        self.merchant_city = self._fmt_struct(60, self.merchant_city)

        self.additional_data_field_value = self._fmt_struct(5, self.transaction_id)
        self.additional_data_field = self._fmt_struct(62, self.additional_data_field_value)

        self.crc16 = '6304'

        print(self.merchant_acc_info)

    def generate_payload(self) -> str:
        self.payload = (
            self.payload_format +
            self.merchant_acc_info +
            self.merchant_category_code +
            self.transaction_currency +
            self.transaction_amount +
            self.country_code +
            self.merchant_name +
            self.merchant_city +
            self.additional_data_field +
            self.crc16
        )
        crc16_func = crcmod.predefined.mkPredefinedCrcFun('crc-ccitt-false')
        crc = crc16_func(self.payload.encode('utf-8'))
        self.payload += f"{crc:04X}"
        return self.payload
    
    def generate_qr_code(self, filename: str = "pix_qr.png"):
        if not hasattr(self, 'payload'):
            self.generate_payload()
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(self.payload)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        img.save(filename)