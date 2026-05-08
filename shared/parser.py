from pathlib import Path

_ROOT = Path(__file__).parent.parent


def parse_stop(stop_str):
    """Parse a single stop string '{key=val}{key=val}...' into a dict."""
    fields = {}
    for field in stop_str.split('}{'):
        if '=' not in field:
            continue
        key, val = field.split('=', 1)
        fields[key] = val
    return fields


def parse_line(line):
    """Parse one line containing multiple stops '{{...}}{{...}}' into a list of dicts."""
    line = line.strip()
    if not line:
        return []
    line = line[2:len(line) - 2]
    return [parse_stop(s) for s in line.split('}}{{')]


def parse_stop_flat(line):
    """Flat version for Spark RDD flatMap — yields tuples, not dicts.
    Returns list of parsed stop dicts from one line."""
    return parse_line(line)
