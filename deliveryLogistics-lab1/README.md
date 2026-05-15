# Lab 1 — Hadoop MapReduce

## Task (Variant 4)

Aggregate data into a table grouped by the `marsrutas` field:
- `svoris` — apply the sum operation
- `siuntu skaicius` — apply the sum operation
- `geografine zona` — create one column per distinct zone value, fill with occurrence frequencies

## Technology

**Hadoop Streaming** — runs Python scripts as mapper and reducer via `stdin` / `stdout`.  
Between Map and Reduce, Hadoop automatically **sorts** all rows by key, guaranteeing that the reducer receives all rows for the same route consecutively.

## Running on Hadoop

```bash
# Upload data to HDFS
hdfs dfs -mkdir -p /input
hdfs dfs -put "Duom Full.txt" /input/

# Submit the MapReduce job
hadoop jar $HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-*.jar \
  -input   /input/"Duom Full.txt" \
  -output  /output \
  -mapper  map.py \
  -reducer red.py \
  -file    map.py \
  -file    red.py

# Download the result
hdfs dfs -get /output/part-00000 result.txt
```

## Local Run (without a cluster)

```bash
python map.py < "Duom Full.txt" > mapout.txt
python Sort.py        # sorts mapout.txt → smapout.txt
python red.py < smapout.txt > redout.txt
```

## Pseudocode

### Input line parsing

```
function parse_line(line):
    strip leading {{ and trailing }} from the line
    split by }}{{ → list of stop strings
    for each stop string:
        split by }{ → list of "key=value" fields
        for each field:
            split by = → key, value
            store in dictionary
    return list of dictionaries
```

### Mapper (map.py)

```
for each line from stdin:
    stops = parse_line(line)
    for each stop in stops:
        extract: marsrutas, svoris (float), siuntu_skaicius (int), geografine_zona
        if all four fields are present:
            emit: marsrutas [TAB] svoris [TAB] siuntu_skaicius [TAB] zona
```

Example mapper output:
```
102    76.0    1    Z1
102    45.0    1    Z1
103    30.0    2    Z2
```

### Shuffle & Sort (Sort.py — local simulation)

```
read all lines from mapout.txt
sort lines by the first field (marsrutas) lexicographically
write sorted lines to smapout.txt
```

> In a real Hadoop cluster this step is performed automatically by the framework.

### Reducer (red.py)

```
ZONES = [Z1, Z2, Z3]

current_route = None
svoris_sum    = 0.0
siuntu_sum    = 0
zone_counts   = { Z1: 0, Z2: 0, Z3: 0 }

print header: marsrutas | svoris_sum | siuntu_sum | Z1 | Z2 | Z3

for each line from stdin:
    parse: route, svoris, siuntu, zona

    if route != current_route:
        if current_route is not None:
            print result row for current_route
        current_route = route
        reset svoris_sum, siuntu_sum, zone_counts to zero

    svoris_sum        += svoris
    siuntu_sum        += siuntu
    zone_counts[zona] += 1

print result row for the last route
```

## Results

| marsrutas | svoris_sum | siuntu_sum | Z1  | Z2 | Z3  |
|-----------|------------|------------|-----|----|-----|
| 102       | 21796.40   | 1939       | 292 | 0  | 5   |
| 103       | 5838.05    | 162        | 33  | 0  | 30  |
| 116       | 7923.92    | 1608       | 209 | 1  | 778 |

**Conclusion:** most routes operate in zone Z1. Route 116 works predominantly in zone Z3. Zone Z2 is almost unused across all routes.
