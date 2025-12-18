import time
from threading import Lock
from functools import wraps

CIRCUIT_THRESHOLD = 2
CIRCUIT_TIMEOUT = 15

_state_lock = Lock()

def circuit_breaker_decorator(func):
    circuit_status = "closed"
    circuit_failures = 0
    circuit_opened_at = None

    def open_circuit():
        nonlocal circuit_status, circuit_opened_at
        circuit_status = "open"
        circuit_opened_at = time.time()
        print(f"Circuit is now OPEN at {time.strftime('%Y-%m-%d %H:%M:%S')}")

    def half_open_circuit():
        nonlocal circuit_status
        circuit_status = "half_open"
        print("Circuit is now HALF-OPEN")

    def close_circuit():
        nonlocal circuit_status, circuit_failures, circuit_opened_at
        circuit_status = "closed"
        circuit_failures = 0
        circuit_opened_at = None
        print("Circuit is now CLOSED")

    def record_failure():
        nonlocal circuit_failures
        circuit_failures += 1
        print(f"Recording failure: {circuit_failures - 1} -> {circuit_failures}")
        if circuit_failures >= CIRCUIT_THRESHOLD:
            open_circuit()

    @wraps(func)
    def wrapper(*args, **kwargs):
        with _state_lock:
            if circuit_status == "open":
                remaining_time = CIRCUIT_TIMEOUT - (time.time() - circuit_opened_at)
                print("Remaining time for circuit to half-open:", remaining_time)
                if remaining_time <= 0:
                    half_open_circuit()
                else:
                    print("Circuit is OPEN: request rejected")
                    return {"message": f"Circuit is open. Try again in {remaining_time:.1f} seconds."}, 503

            if circuit_status == "half_open":
                print("Circuit is HALF-OPEN: trial")

        try:
            result = func(*args, **kwargs)

            with _state_lock:
                if circuit_status == "half_open":
                    print("Successful trial in HALF-OPEN: closing circuit")
                    close_circuit()

            return result

        except Exception as e:
            with _state_lock:
                if circuit_status == "half_open":
                    print("Failure in HALF-OPEN: reopening circuit")
                    open_circuit()
                else:
                    record_failure()

            return {"message": "Internal error during processing.", "error": str(e)}, 500

    return wrapper
