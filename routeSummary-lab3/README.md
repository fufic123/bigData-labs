# Lab 3 — Apache Spark DataFrame + Spark ML

## Task (Variant 4)

Investigate the linear relationship between `BendrasLaikas` (total route duration) and `svoris` (parcel weight, aggregated as sum per route per day), considering only routes that used exactly one vehicle type (`Masinos tipas`) on a given day. Apply linear regression.

## Technology

**Apache Spark, DataFrame API + Spark ML.**

- **DataFrame** — a distributed table with a typed schema, optimised by Spark's Catalyst query planner (similar to SQL or pandas, but runs on a cluster).
- **Spark ML** — Spark's machine learning library. Requires features packed into a single `Vector` column and a `Double` label column.

## Data Sources

| File | Contents |
|------|----------|
| `Duom Full.txt` | Raw stop-level records (one line = one route-day, multiple stops per line) |
| `RouteSummary.txt` | Pre-aggregated route-day summary: `marsrutas`, `sustojimo data`, `BendrasLaikas`, etc. |

## Running

```bash
pip install pyspark
spark-submit routeSummary-lab3/main.py
# or simply:
python routeSummary-lab3/main.py
```

## Pseudocode

```
CREATE SparkSession

// ── Part 1: stops data ────────────────────────────────────────────────

// Load and parse raw stops into a DataFrame
stops_rdd = sc.textFile(STOPS_DATA).flatMap(parse_line)
stops_df  = createDataFrame(
    stops_rdd
        .filter(stop has marsrutas, sustojimo data, Masinos tipas, svoris)
        .map(stop → (marsrutas, sustojimo_data, Masinos_tipas, float(svoris))),
    schema = [marsrutas, sustojimo_data, Masinos_tipas, svoris]
)

// Keep only route-days that used exactly one vehicle type
single_vehicle = stops_df
    .groupBy(marsrutas, sustojimo_data)
    .agg(countDistinct(Masinos_tipas) AS n_vehicles)
    .filter(n_vehicles == 1)

// Sum weight per route-day, then inner-join to keep only single-vehicle days
svoris_agg = stops_df
    .groupBy(marsrutas, sustojimo_data)
    .agg(sum(svoris) AS svoris_sum)
    .join(single_vehicle, on=[marsrutas, sustojimo_data])
    .select(marsrutas, sustojimo_data, svoris_sum)

// ── Part 2: route summary data ────────────────────────────────────────

function time_to_minutes(t):          // UDF registered in Spark
    strip quotes from t               // e.g. "02:15" → 02:15
    split by : → hours, minutes
    return hours * 60 + minutes       // 02:15 → 135.0

summary = read_csv(ROUTE_SUMMARY, header=True)
    .select(marsrutas, sustojimo_data, BendrasLaikas)
    .withColumn(laikas_min, time_to_minutes(BendrasLaikas).cast(Double))

// ── Part 3: join and train ────────────────────────────────────────────

joined = svoris_agg.join(summary, on=[marsrutas, sustojimo_data]).dropna()

// Spark ML requires all features in one Vector column
assembler = VectorAssembler(inputCols=[svoris_sum], outputCol=features)
ml_data   = assembler.transform(joined)
              .select(features, laikas_min AS label)

// Fit linear regression: label = b0 + b1 * features
model = LinearRegression(featuresCol=features, labelCol=label).fit(ml_data)

// ── Part 4: print results ─────────────────────────────────────────────

print intercept    : model.intercept          // b0 (minutes)
print coefficient  : model.coefficients[0]   // b1 (minutes per kg)
print RMSE         : model.summary.rootMeanSquaredError
print R²           : model.summary.r2
print formula      : BendrasLaikas = b0 + b1 * svoris_sum

STOP SparkSession
```

### Key steps explained

| Step | Why |
|------|-----|
| `countDistinct(Masinos_tipas) == 1` | Removes mixed-vehicle days to keep data consistent for regression |
| `inner join` with `single_vehicle` | Acts as a filter — only matching rows are kept |
| UDF `time_to_minutes` | Converts `"HH:MM"` string to a numeric value usable by ML |
| `VectorAssembler` | Spark ML requires a single `Vector` column for features, even with one feature |
| `LinearRegression.fit()` | Finds coefficients b0, b1 minimising mean squared error |

## Results

```
BendrasLaikas = b0 + b1 * svoris_sum

Intercept  (b0): ~240 minutes
Coefficient (b1): very small (near zero)
RMSE:             high
R²:               0.012
Training samples: ...
```

**Conclusion:** R² = 0.012 means the model explains only **1.2% of the variance** in route duration. There is no meaningful linear relationship between total parcel weight and total route time. This is expected — route duration depends primarily on the number of stops, distances between them, and traffic conditions, not on how heavy the parcels are.
