# utils.py
import math


def format_runtime(runtime):
    """Format media runtime minutes to hours format for readability"""
    num_of_hours = runtime / 60
    hours = math.floor(num_of_hours)
    minutes = runtime - (hours * 60)

    return f"{hours}h {minutes}m"
