

class HabitTrackerError(Exception):
    """Base exception for all Habit Tracker errors."""
    pass


class InvalidHabitError(HabitTrackerError):
    """Raised when habit data is invalid (e.g. empty name, bad frequency)."""
    pass


class StorageError(HabitTrackerError):
    """Raised when a file read or write operation fails."""
    pass
