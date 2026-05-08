#!/usr/bin/env python3
import sys

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    line = line[2:len(line) - 2]
    stops = line.split('}}{{')

    for stop in stops:
        marsrutas = None
        svoris = None
        siuntu_skaicius = None
        zona = None

        for field in stop.split('}{'):
            if '=' not in field:
                continue
            key, val = field.split('=', 1)
            if key == 'marsrutas' and val:
                marsrutas = val
            elif key == 'svoris' and val:
                try:
                    svoris = float(val)
                except ValueError:
                    pass
            elif key == 'siuntu skaicius' and val:
                try:
                    siuntu_skaicius = int(val)
                except ValueError:
                    pass
            elif key == 'geografine zona' and val:
                zona = val

        if marsrutas and svoris is not None and siuntu_skaicius is not None and zona:
            print('%s\t%s\t%s\t%s' % (marsrutas, svoris, siuntu_skaicius, zona))
