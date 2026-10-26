from models import Habit
from storage import HabitStorage
from decorators import log_action, require_habits
from exceptions import InvalidHabitError, StorageError
from utils import (
    validate_time_format, validate_day, format_name,
    generate_habit_report, VALID_DAYS, get_today
)


storage = HabitStorage()
habits = []

DEFAULT_TEMPLATES = [
    {
        "name": "Gym",
        "description": "Go to the gym for a workout session",
        "preferred_times": ["07:00"],
        "preferred_days": ["Every Day"],
    },
    {
        "name": "Watermaxxing",
        "description": "Drink at least 8 glasses of water",
        "preferred_times": ["08:00"],
        "preferred_days": ["Every Day"],
    },
    {
        "name": "Read",
        "description": "Read for at least 30 minutes",
        "preferred_times": ["21:00"],
        "preferred_days": ["Every Day"],
    },
    {
        "name": "Meditate",
        "description": "Meditate for 10 minutes",
        "preferred_times": ["07:30"],
        "preferred_days": ["Every Day"],
    },
    {
        "name": "Clean Air Maxxing",
        "description": "Go for a 30-minute walk outside",
        "preferred_times": ["18:00"],
        "preferred_days": ["Every Day"],
    },
]


def display_main_menu():
    print()
    print("  [ HABIT TRACKER ]")
    print()
    print("  1. View my habits")
    print("  2. Add habit")
    print("  3. Log completion")
    print("  4. View progress")
    print("  5. Remove habit")
    print("  6. Edit habit")
    print("  7. View notes")
    print("  8. Exit")
    print()


def display_habits_list():
    if not habits:
        print("\n  You have no habits yet. Add one from the menu.")
        return

    streaks = {h.name: h.get_streak() for h in habits}

    print()
    print(f"  {'':3} {'HABIT':<22} {'STREAK':>6}   {'LAST DONE':>10}")

    for habit in habits:
        tag = "[D]" if habit.is_default else "[C]"
        streak = streaks[habit.name]
        last = habit.get_last_log()
        last_date = last.date if last else "Never"
        print(f"  {tag} {habit.name:<22} {streak:>4} day(s)   {last_date}")

    print("  [D] Default    [C] Custom")


@log_action
def add_habit_menu():
    print()
    print("  [ ADD HABIT ]")
    print()
    print("  1. Choose from default habits")
    print("  2. Create custom habit")
    print("  0. Back")

    choice = input("\n  Select: ").strip()

    if choice == "1":
        add_default_habit()
    elif choice == "2":
        add_custom_habit()
    elif choice == "0":
        return
    else:
        print("  Invalid option.")


def add_default_habit():
    print()
    print("  [ DEFAULT HABITS ]")
    print()

    added_names = {h.name for h in habits if h.is_default}
    available = [t for t in DEFAULT_TEMPLATES if t["name"] not in added_names]

    if not available:
        print("  You already have all default habits!")
        return

    for i, template in enumerate(available, 1):
        times_str = ", ".join(template['preferred_times']) if template['preferred_times'] else "N/A"
        days_str = ", ".join(template['preferred_days']) if template['preferred_days'] else "N/A"
        print(f"  {i}. {template['name']}")
        print(f"     {template['description']}")
        print(f"     Time(s): {times_str}  |  Day(s): {days_str}")
        print()

    print("  0. Back")

    try:
        choice = int(input("  Select: ").strip())

        if choice == 0:
            return

        if 1 <= choice <= len(available):
            t = available[choice - 1]

            print(f"\n  Customise times for '{t['name']}' (press Enter to keep defaults).")
            print("  Enter preferred time(s) one by one (e.g. 07:30). Press Enter with no input when done.")
            preferred_times = []
            while True:
                time_input = input(f"  Time {len(preferred_times)+1} (Enter to finish): ").strip()
                if not time_input:
                    break
                if validate_time_format(time_input):
                    preferred_times.append(time_input)
                else:
                    print("  Invalid format. Use HH:MM, for example 07:30.")
            if not preferred_times:
                preferred_times = t["preferred_times"]

            print(f"\n  Valid days: {', '.join(VALID_DAYS)}")
            print("  Enter preferred day(s) one by one. Press Enter with no input when done.")
            preferred_days = []
            while True:
                day_input = input(f"  Day {len(preferred_days)+1} (Enter to finish): ").strip()
                if not day_input:
                    break
                if validate_day(day_input):
                    preferred_days.append(day_input.strip().title())
                else:
                    print("  Invalid day. Choose a weekday name or 'Every Day'.")
            if not preferred_days:
                preferred_days = t["preferred_days"]

            new_habit = Habit(
                name=t["name"],
                description=t["description"],
                preferred_times=preferred_times,
                preferred_days=preferred_days,
                is_default=True,
            )
            habits.append(new_habit)
            storage.save(habits)
            print(f"\n  '{new_habit.name}' added to your habits!")
        else:
            print("  Invalid number.")

    except ValueError:
        print("  Please enter a valid number.")


def add_custom_habit():
    print()
    print("  [ CUSTOM HABIT ]")
    print()

    name = input("  Name: ").strip()
    if not name:
        print("  Name cannot be empty.")
        return

    if any(h.name.lower() == name.lower() for h in habits):
        print(f"  A habit named '{name}' already exists.")
        return

    description = input("  Description (Enter to skip): ").strip()

    preferred_times = []
    print("  Enter preferred time(s) one by one (e.g. 07:30). Press Enter with no input when done.")
    while True:
        time_input = input(f"  Time {len(preferred_times)+1} (Enter to finish): ").strip()
        if not time_input:
            break
        if validate_time_format(time_input):
            preferred_times.append(time_input)
        else:
            print("  Invalid format. Use HH:MM, for example 07:30.")

    preferred_days = []
    print(f"\n  Valid days: {', '.join(VALID_DAYS)}")
    print("  Enter preferred day(s) one by one. Press Enter with no input when done.")
    while True:
        day_input = input(f"  Day {len(preferred_days)+1} (Enter to finish): ").strip()
        if not day_input:
            break
        if validate_day(day_input):
            preferred_days.append(day_input.strip().title())
        else:
            print("  Invalid day. Choose a weekday name or 'Every Day'.")

    try:
        new_habit = Habit(
            name=format_name(name),
            description=description,
            preferred_times=preferred_times,
            preferred_days=preferred_days,
            is_default=False,
        )
        habits.append(new_habit)
        storage.save(habits)
        print(f"\n  '{new_habit.name}' added to your habits!")

    except InvalidHabitError as e:
        print(f"  Error: {e}")


@require_habits
@log_action
def log_completion(habits):
    print()
    print("  [ LOG COMPLETION ]")
    print()

    today = get_today()

    for i, habit in enumerate(habits, 1):
        already_done = any(log.date == today for log in habit.logs)
        status = "  (done today)" if already_done else ""
        print(f"  {i}. {habit.name}{status}")

    print("  0. Back")

    try:
        choice = int(input("\n  Select habit: ").strip())

        if choice == 0:
            return

        if 1 <= choice <= len(habits):
            habit = habits[choice - 1]
            note = input("  Add a note (Enter to skip): ").strip()

            if habit.log_completion(note=note or None):
                storage.save(habits)
                streak = habit.get_streak()
                print(f"\n  Logged '{habit.name}' for today!")
                print(f"  Current streak: {streak} day(s)")
            else:
                print(f"\n  '{habit.name}' was already logged today.")
        else:
            print("  Invalid number.")

    except ValueError:
        print("  Please enter a valid number.")


@require_habits
@log_action
def view_progress(habits):
    print()
    print("  [ VIEW PROGRESS ]")
    print()

    for i, habit in enumerate(habits, 1):
        print(f"  {i}. {habit.name}")

    print("  0. Back")

    try:
        choice = int(input("\n  Select habit: ").strip())

        if choice == 0:
            return

        if 1 <= choice <= len(habits):
            habit = habits[choice - 1]

            print()
            print("  [ PROGRESS REPORT ]")
            print()

            for report_line in generate_habit_report(habit):
                print(report_line)

            print()
        else:
            print("  Invalid number.")

    except ValueError:
        print("  Please enter a valid number.")


@require_habits
@log_action
def remove_habit(habits):
    print()
    print("  [ REMOVE HABIT ]")
    print()

    for i, habit in enumerate(habits, 1):
        print(f"  {i}. {habit.name}")

    print("  0. Back")

    try:
        choice = int(input("\n  Select to remove: ").strip())

        if choice == 0:
            return

        if 1 <= choice <= len(habits):
            habit = habits[choice - 1]
            confirm = input(f"  Remove '{habit.name}'? (yes/no): ").strip().lower()

            if confirm == "yes":
                habits.remove(habit)
                storage.save(habits)
                print(f"\n  '{habit.name}' removed.")
            else:
                print("  Cancelled.")
        else:
            print("  Invalid number.")

    except ValueError:
        print("  Please enter a valid number.")


@require_habits
@log_action
def edit_habit(habits):
    print()
    print("  [ EDIT HABIT ]")
    print()

    for i, habit in enumerate(habits, 1):
        print(f"  {i}. {habit.name}")

    print("  0. Back")

    try:
        choice = int(input("\n  Select habit to edit: ").strip())

        if choice == 0:
            return

        if 1 <= choice <= len(habits):
            habit = habits[choice - 1]

            print(f"\n  Editing '{habit.name}' — press Enter to keep current value.")
            print()

            new_name = input(f"  Name [{habit.name}]: ").strip()
            if new_name:
                if any(h.name.lower() == new_name.lower() for h in habits if h is not habit):
                    print("  A habit with that name already exists. Name not changed.")
                else:
                    habit.name = format_name(new_name)

            new_desc = input(f"  Description [{habit.description or 'N/A'}]: ").strip()
            if new_desc:
                habit.description = new_desc

            times_str = ", ".join(habit.preferred_times) if habit.preferred_times else "N/A"
            print(f"\n  Current time(s): {times_str}")
            print("  Enter new time(s) one by one, or press Enter immediately to keep current.")
            new_times = []
            while True:
                time_input = input(f"  Time {len(new_times)+1} (Enter to finish): ").strip()
                if not time_input:
                    break
                if validate_time_format(time_input):
                    new_times.append(time_input)
                else:
                    print("  Invalid format. Use HH:MM, for example 07:30.")
            if new_times:
                habit.preferred_times = new_times

            days_str = ", ".join(habit.preferred_days) if habit.preferred_days else "N/A"
            print(f"\n  Current day(s): {days_str}")
            print(f"  Valid days: {', '.join(VALID_DAYS)}")
            print("  Enter new day(s) one by one, or press Enter immediately to keep current.")
            new_days = []
            while True:
                day_input = input(f"  Day {len(new_days)+1} (Enter to finish): ").strip()
                if not day_input:
                    break
                if validate_day(day_input):
                    new_days.append(day_input.strip().title())
                else:
                    print("  Invalid day. Choose a weekday name or 'Every Day'.")
            if new_days:
                habit.preferred_days = new_days

            storage.save(habits)
            print(f"\n  '{habit.name}' updated!")
        else:
            print("  Invalid number.")

    except ValueError:
        print("  Please enter a valid number.")


@require_habits
@log_action
def view_notes(habits):
    print()
    print("  [ VIEW NOTES ]")
    print()

    for i, habit in enumerate(habits, 1):
        notes_count = sum(1 for log in habit.logs if log.note)
        print(f"  {i}. {habit.name}  ({notes_count} note(s))")

    print("  0. Back")

    try:
        choice = int(input("\n  Select habit: ").strip())

        if choice == 0:
            return

        if 1 <= choice <= len(habits):
            habit = habits[choice - 1]

            logs_with_notes = [log for log in habit.logs if log.note]

            print()
            print(f"  [ NOTES — {habit.name.upper()} ]")
            print()

            if not logs_with_notes:
                print("  No notes recorded for this habit.")
                return

            logs_with_notes.sort(key=lambda log: (log.date, log.time), reverse=True)

            for log in logs_with_notes:
                print(f"  {log.date} at {log.time}")
                print(f"  → {log.note}")
                print()

        else:
            print("  Invalid number.")

    except ValueError:
        print("  Please enter a valid number.")


def load_habits():
    global habits
    try:
        habits = storage.load()
        print(f"  Loaded {len(habits)} habit(s).")
    except StorageError as e:
        print(f"  Warning: {e}")
        habits = []


def main():
    print("\n  Welcome to Habit Tracker!")
    load_habits()

    while True:
        display_main_menu()
        choice = input("  Select (1-8): ").strip()

        if choice == "1":
            display_habits_list()
        elif choice == "2":
            add_habit_menu()
        elif choice == "3":
            log_completion(habits)
        elif choice == "4":
            view_progress(habits)
        elif choice == "5":
            remove_habit(habits)
        elif choice == "6":
            edit_habit(habits)
        elif choice == "7":
            view_notes(habits)
        elif choice == "8":
            print("\n  Goodbye!\n")
            break
        else:
            print("\n  Please select a number between 1 and 8.")


if __name__ == "__main__":
    main()