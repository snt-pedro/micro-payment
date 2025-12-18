import time
from functools import wraps

def retry_decorator(max_retries=3, delay=2):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    print(f"Attempt {attempts} failed: {e}")
                    if attempts < max_retries:
                        time.sleep(delay)
            print("All retry attempts failed.")
            return {"message": f"Operation failed after {max_retries} retries."}, 500
        return wrapper
    return decorator