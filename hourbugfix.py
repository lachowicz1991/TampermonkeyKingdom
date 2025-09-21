from datetime import datetime


def time_fix_decorator(func):
    def wrapper(t1: str, t2: str, *args, **kwargs):
        fixed_t1 = fix_time_bug(t1, t2)
        return func(fixed_t1, t2, *args, **kwargs)
    return wrapper

def fix_time_bug(t1: str, t2: str, tolerance_sec: int = 600) -> str:
    fmt = "%H:%M:%S.%f"
    dt1 = datetime.strptime(t1, fmt)
    dt2 = datetime.strptime(t2, fmt)

    # Seconds-of-day helpers (use milliseconds to avoid float)
    def to_ms(h, m, s, us):
        return ((h*60 + m)*60 + s)*1000 + (us // 1000)

    def circ_diff_ms(a, b):
        day = 24 * 3600 * 1000
        d = abs(a - b)
        return min(d, day - d)

    t2_ms = to_ms(dt2.hour, dt2.minute, dt2.second, dt2.microsecond)

    best = None
    best_diff = float("inf")

    for k in (-3, -2, -1, 0, 1, 2, 3):
        cand_hour = (dt1.hour + k) % 24
        cand_ms = to_ms(cand_hour, dt1.minute, dt1.second, dt1.microsecond)
        diff = circ_diff_ms(cand_ms, t2_ms)
        if diff < best_diff:
            best_diff = diff
            best = cand_hour

    # If the closest candidate is within tolerance, return it; else keep original t1
    if best_diff <= tolerance_sec * 1000:
        # format back to "HH:MM:SS.mmm" (3-digit millis)
        return f"{best:02d}:{dt1.minute:02d}:{dt1.second:02d}.{dt1.microsecond//1000:03d}"
    else:
        return f"{dt1.hour:02d}:{dt1.minute:02d}:{dt1.second:02d}.{dt1.microsecond//1000:03d}"


@time_fix_decorator
def time_diff_ms(t1: str, t2: str) -> int:
    fmt = "%H:%M:%S.%f"
    dt1 = datetime.strptime(t1, fmt)
    dt2 = datetime.strptime(t2, fmt)

    time_difference = int((dt1 - dt2).total_seconds() * 1000)
    if time_difference <= 10000:
        return time_difference
    else:
        return time_difference



#Test
print(time_diff_ms("05:55:07.233", "05:55:00.233"))  # -> 07:55:10.233
print(time_diff_ms("08:50:06.000", "07:50:01.000"))  # -> 08:01:10.233
print(time_diff_ms("10:01:10.233", "07:59:01.233"))  # -> 08:01:10.233  (fixed from wrong hour)
