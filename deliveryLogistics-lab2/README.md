# Lab 2 — Apache Spark RDD

## Task (Variant 1)

Calculate the minimum, maximum, and arithmetic mean of parcel weight (`svoris`) across different weight groups (`svorio grupe`).

## Technology

**Apache Spark, RDD API.**  
RDD (Resilient Distributed Dataset) is Spark's core abstraction — an immutable distributed collection split into partitions processed in parallel.

Operations are split into:
- **Transformations** (lazy, build a DAG): `map`, `filter`, `flatMap`, `mapValues`, `reduceByKey`, `sortByKey`
- **Actions** (trigger execution): `collect`, `count`, `take`

## Running

```bash
pip install pyspark
spark-submit deliveryLogistics-lab2/main.py
# or simply:
python deliveryLogistics-lab2/main.py
```

## Pseudocode

```
CREATE SparkContext

// Step 1 — load and parse
lines = sc.textFile(STOPS_DATA)
stops = lines.flatMap(parse_line)
    // each line → list of stop dicts → flattened into one RDD

// Step 2 — filter and extract fields
weight_pairs = stops
    .filter(stop has non-empty 'svorio grupe' and 'svoris')
    .map(stop → (stop['svorio grupe'], float(stop['svoris'])))
    // result: RDD of (group_string, weight_float)
    // e.g. ('<50', 45.0), ('<300', 76.0), ('>300', 764.2)

// Step 3 — aggregate per group
//   represent each weight as a tuple (min, max, sum, count)
accum = weight_pairs
    .mapValues(w → (w, w, w, 1))

//   merge two accumulators for the same key:
function merge(a, b):
    return (min(a.min, b.min),
            max(a.max, b.max),
            a.sum + b.sum,
            a.count + b.count)

aggregated = accum.reduceByKey(merge)
    // reduceByKey combines values locally on each executor first,
    // then across executors — avoids shuffling all raw values over network

// Step 4 — compute average and format
results = aggregated
    .mapValues((mn, mx, s, n) → (mn, mx, s / n))
    .sortByKey()
    .collect()

// Step 5 — print
for each (group, (min, max, avg)) in results:
    print group, min, max, avg

STOP SparkContext
```

### Why `reduceByKey` instead of `groupByKey`

`groupByKey` collects **all raw values** for a key onto one node before aggregating — can cause out-of-memory errors on large data.  
`reduceByKey` applies the merge function **locally on each executor** first, then merges partial results across the network. Only small aggregated tuples are transferred, not all raw weights.

## Results

| svorio grupe | min  | max      | avg    |
|--------------|------|----------|--------|
| <50          | 0.00 | 49.99    | 18.75  |
| <300         | 0.00 | 299.99   | 93.40  |
| >300         | 300.00 | 12500.00 | 621.33 |

**Conclusion:** the `>300` group has a very high average (621 kg) and a wide range up to 12 500 kg, indicating the presence of large bulk shipments. The `<50` group has a low average weight of 18.75 kg, typical for standard parcel deliveries.
