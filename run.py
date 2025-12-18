import os
from app import app as application
from dotenv import load_dotenv

load_dotenv()

FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
FLASK_PORT = os.getenv("FLASK_PORT", 5001)

if __name__ == "__main__":
    application.run(host=FLASK_HOST, port=FLASK_PORT, debug=True)