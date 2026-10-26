from functools import wraps
from datetime import datetime


def log_action(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"  [{timestamp}] {func.__name__.replace('_', ' ').title()}")
        return func(*args, **kwargs)
    return wrapper


def require_habits(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        habits_list = args[0] if args else []
        if not habits_list:
            print("\n  No habits added yet. Use 'Add habit' first.")
            return None
        return func(*args, **kwargs)
    return wrapper
