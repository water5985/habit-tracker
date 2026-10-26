import json
from pathlib import Path
from models import Habit
from exceptions import StorageError


class HabitStorage:

    def __init__(self, filename="data/habits.json"):
        self.filename = filename
        self._ensure_directory()

    def _ensure_directory(self):
        Path(self.filename).parent.mkdir(parents=True, exist_ok=True)

    def load(self):

        try:
            if Path(self.filename).exists():
                with open(self.filename, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return [Habit.from_dict(item) for item in data]
            return []
        except json.JSONDecodeError:
            raise StorageError(
                f"File '{self.filename}' contains invalid JSON and could not be read."
            )
        except Exception as e:
            raise StorageError(f"Could not load habits: {e}")

    def save(self, habits):
        try:
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump(
                    [habit.to_dict() for habit in habits],
                    f,
                    indent=2,
                    ensure_ascii=False
                )
        except Exception as e:
            raise StorageError(f"Could not save habits: {e}")
