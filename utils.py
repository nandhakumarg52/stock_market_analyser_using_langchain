from functools import wraps
import traceback
from requests.exceptions import RequestException


def safe_execute(fn):
    """
    Decorator to safely execute tools and return structured errors.
    """
    @wraps(fn)   # 🔥 THIS IS THE FIX
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except RequestException as e:
            return {
                "status": "error",
                "type": "API_ERROR",
                "message": str(e)
            }
        except ValueError as e:
            return {
                "status": "error",
                "type": "VALUE_ERROR",
                "message": str(e)
            }
        except Exception as e:
            return {
                "status": "error",
                "type": "INTERNAL_ERROR",
                "message": str(e),
                "trace": traceback.format_exc()
            }
    return wrapper
