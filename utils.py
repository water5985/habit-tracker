import re
from datetime import datetime


VALID_DAYS = [
    "Monday", "Tuesday", "Wednesday", "Thursday",
    "Friday", "Saturday", "Sunday", "Every Day"
]

format_name = lambda name: name.strip().title()


def validate_time_format(time_str):

    if not time_str:
        return True
    pattern = r'^([01]\d|2[0-3]):([0-5]\d)$'
    return bool(re.match(pattern, time_str))


def validate_day(day_str):
    if not day_str:
        return True
    return day_str.strip().title() in VALID_DAYS


def get_today():
    return datetime.now().strftime("%Y-%m-%d")


def get_current_time():
    return datetime.now().strftime("%H:%M")


def generate_habit_report(habit):
    yield f"  Name        : {habit.name}"
    yield f"  Type        : {'Default' if habit.is_default else 'Custom'}"
    yield f"  Description : {habit.description if habit.description else 'N/A'}"
    times_str = ", ".join(habit.preferred_times) if habit.preferred_times else "N/A"
    yield f"  Pref. times : {times_str}"
    days_str = ", ".join(habit.preferred_days) if habit.preferred_days else "N/A"
    yield f"  Pref. days  : {days_str}"
    yield f"  Added on    : {habit.created_date}"
    yield f"  Streak      : {habit.get_streak()} day(s)"
    yield f"  Total done  : {habit.get_total_completions()} time(s)"

    last = habit.get_last_log()
    if last:
        note_part = f"  —  note: {last.note}" if last.note else ""
        yield f"  Last done   : {last.date} at {last.time}{note_part}"
    else:
        yield f"  Last done   : Never"
