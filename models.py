from datetime import datetime
from exceptions import InvalidHabitError
import uuid


class HabitLog:

    def __init__(self, date=None, time=None, note=None):
        self.date = date or datetime.now().strftime("%Y-%m-%d")
        self.time = time or datetime.now().strftime("%H:%M")
        self.note = note or ""

    def to_dict(self):
        return {
            "date": self.date,
            "time": self.time,
            "note": self.note
        }

    @staticmethod
    def from_dict(data):
        log = HabitLog()
        log.date = data["date"]
        log.time = data["time"]
        log.note = data.get("note", "")
        return log


class Habit:

    def __init__(self, name, description="", preferred_times=None,
                 preferred_days=None, is_default=False):
        if not name or not isinstance(name, str):
            raise InvalidHabitError("Habit name must be a non-empty string.")

        self.id = str(uuid.uuid4())[:8]
        self.name = name.strip()
        self.description = description.strip()
        self.preferred_times = preferred_times or []
        self.preferred_days = preferred_days or []
        self.is_default = is_default
        self.created_date = datetime.now().strftime("%Y-%m-%d")
        self.logs = []


    def log_completion(self, note=None):

        today = datetime.now().strftime("%Y-%m-%d")

        if any(log.date == today for log in self.logs):
            return False

        self.logs.append(HabitLog(note=note))
        return True


    def get_streak(self):
        if not self.logs:
            return 0

        today = datetime.now().date()

        unique_dates = {
            datetime.strptime(log.date, "%Y-%m-%d").date()
            for log in self.logs
        }

        log_dates = sorted(unique_dates, reverse=True)

        days_since_last = (today - log_dates[0]).days
        if days_since_last > 1:
            return 0

        streak = 1
        for i in range(1, len(log_dates)):
            diff = (log_dates[i - 1] - log_dates[i]).days
            if diff == 1:
                streak += 1
            else:
                break

        return streak

    def get_last_log(self):
        if not self.logs:
            return None

        return max(self.logs, key=lambda log: (log.date, log.time))

    def get_total_completions(self):
        return len(self.logs)


    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "preferred_times": self.preferred_times,
            "preferred_days": self.preferred_days,
            "is_default": self.is_default,
            "created_date": self.created_date,
            "logs": [log.to_dict() for log in self.logs]
        }

    @staticmethod
    def from_dict(data):
        def normalize_list(value):
            if not value:
                return []
            if isinstance(value, str):
                return [value]

            result = []
            for item in value:
                result.extend(normalize_list(item))
            return result

        habit = Habit(
            name=data["name"],
            description=data.get("description", ""),
            preferred_times=normalize_list(
                data.get("preferred_times", data.get("preferred_time", []))
            ),
            preferred_days=normalize_list(
                data.get("preferred_days", data.get("preferred_day", []))
            ),
            is_default=data.get("is_default", False)
        )

        habit.id = data["id"]
        habit.created_date = data["created_date"]
        habit.logs = [
            HabitLog.from_dict(log)
            for log in data.get("logs", [])
        ]
        return habit