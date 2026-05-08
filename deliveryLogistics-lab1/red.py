#!/usr/bin/env python3
import sys

ZONES = ['Z1', 'Z2', 'Z3']

print('marsrutas\tsvoris_sum\tsiuntu_sum\t' + '\t'.join(ZONES))

current_route = None
svoris_sum = 0.0
siuntu_sum = 0
zone_counts = {z: 0 for z in ZONES}


def flush(route):
    counts = '\t'.join(str(zone_counts[z]) for z in ZONES)
    print('%s\t%.2f\t%d\t%s' % (route, svoris_sum, siuntu_sum, counts))


for line in sys.stdin:
    line = line.strip()
    parts = line.split('\t')
    if len(parts) != 4:
        continue

    route, svoris, siuntu, zona = parts

    try:
        svoris = float(svoris)
        siuntu = int(siuntu)
    except ValueError:
        continue

    if route != current_route:
        if current_route is not None:
            flush(current_route)
        current_route = route
        svoris_sum = 0.0
        siuntu_sum = 0
        zone_counts = {z: 0 for z in ZONES}

    svoris_sum += svoris
    siuntu_sum += siuntu
    if zona in zone_counts:
        zone_counts[zona] += 1

if current_route is not None:
    flush(current_route)
