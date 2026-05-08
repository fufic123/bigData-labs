import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from pyspark import SparkContext
from shared.parser import parse_line
from shared.paths import STOPS_DATA


def main():
    sc = SparkContext(appName='Lab2-Task1')
    sc.setLogLevel('ERROR')

    stops = sc.textFile(STOPS_DATA).flatMap(parse_line)

    weight_pairs = (
        stops
        .filter(lambda s: s.get('svorio grupe') and s.get('svoris'))
        .map(lambda s: (s['svorio grupe'], float(s['svoris'])))
    )

    def merge(a, b):
        return (min(a[0], b[0]), max(a[1], b[1]), a[2] + b[2], a[3] + b[3])

    results = (
        weight_pairs
        .mapValues(lambda w: (w, w, w, 1))
        .reduceByKey(merge)
        .mapValues(lambda v: (v[0], v[1], v[2] / v[3]))
        .sortByKey()
        .collect()
    )

    print(f'\n{"svorio grupe":<12} {"min":>10} {"max":>10} {"avg":>10}')
    print('-' * 46)
    for group, (mn, mx, avg) in results:
        print(f'{group:<12} {mn:>10.2f} {mx:>10.2f} {avg:>10.2f}')

    sc.stop()


if __name__ == '__main__':
    main()
