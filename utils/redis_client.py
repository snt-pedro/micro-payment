import os
import redis
from dotenv import load_dotenv

load_dotenv()

REDIS_SOCKET_TIMEOUT = float(os.getenv("REDIS_SOCKET_TIMEOUT", 1.0))
REDIS_CONNECT_TIMEOUT = float(os.getenv("REDIS_CONNECT_TIMEOUT", 0.5))
REDIS_RETRY_ON_TIMEOUT = os.getenv("REDIS_RETRY_ON_TIMEOUT", "true").lower() in ("1", "true", "yes")

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6380)),
    db=int(os.getenv("REDIS_DB", 0)),
    decode_responses=True,
    socket_timeout=REDIS_SOCKET_TIMEOUT,
    socket_connect_timeout=REDIS_CONNECT_TIMEOUT,
    retry_on_timeout=REDIS_RETRY_ON_TIMEOUT,
)
