from datetime import datetime, timedelta


def last_n_days(n: int, use_current_time: bool = True) -> tuple:
    """
    Returns a tuple of two datetime objects representing the start and end time
    for the last n days. If use_current_time is True, the end time is set to
    the current time. If False, the end time is set to the start of the current day.
    """
    now = datetime.now(datetime.timezone.utc)
    end_time = (
        now
        if use_current_time
        else now.replace(hour=0, minute=0, second=0, microsecond=0)
    )
    start_time = end_time - timedelta(days=n)
    return start_time, end_time
