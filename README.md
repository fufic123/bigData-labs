# BigData Labs

Laboratory works for the Big Data Processing course. All labs analyze delivery driver stop data from a parcel logistics company.

## Dataset

The main dataset (`deliveryLogistics-lab1/Duom Full.zip`) contains semi-structured records of delivery stops with ~26 fields per stop: route, date, weight, parcel count, geographical zone, vehicle type, etc.

The secondary dataset (`routeSummary-lab3/RouteSummary.txt`) contains per-route daily summaries: total distance, weight, time, and cost.

## Labs

### Lab 1 — Hadoop MapReduce

**Task 4:** Aggregate data grouped by `marsrutas` (route): sum of `svoris` (weight), sum of `siuntu skaicius` (parcels), and stop frequency per geographical zone (Z1/Z2/Z3).

**Run:**
```bash
cd deliveryLogistics-lab1
unzip "Duom Full.zip"

hadoop jar /opt/homebrew/opt/hadoop/libexec/share/hadoop/tools/lib/hadoop-streaming-*.jar \
  -files map.py,red.py \
  -mapper "python3 map.py" \
  -reducer "python3 red.py" \
  -input "Duom Full.txt" \
  -output output
```

### Lab 2 — Apache Spark (RDD)

**Task 1:** Calculate minimum, maximum, and average parcel weight (`svoris`) per weight group (`svorio grupe`).

**Run:**
```bash
source venv/bin/activate
python3 deliveryLogistics-lab2/main.py
```

**Result:**

| svorio grupe | min (kg) | max (kg) | avg (kg) |
|---|---|---|---|
| `<50` | 0.00 | 50.00 | 5.96 |
| `<300` | 50.05 | 300.00 | 110.03 |
| `>300` | 300.05 | 6896.65 | 759.21 |

### Lab 3 — Apache Spark (DataFrame + ML)

**Task 4:** Investigate the linear relationship between `BendrasLaikas` (total route time) and the sum of `svoris` (weight), considering only routes with a single vehicle type (`Masinos tipas`) per day. Uses Spark ML linear regression.

**Run:**
```bash
source venv/bin/activate
python3 routeSummary-lab3/main.py
```

**Result:**
```
BendrasLaikas = 506.29 + 0.008647 * svoris_sum
R² = 0.012  — weak linear relationship
```

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Java 17 is required for Spark and Hadoop:
```bash
brew install openjdk@17
export JAVA_HOME=/opt/homebrew/opt/openjdk@17
```

## Structure

```
bigData/
├── venv/                            # shared virtual environment
├── requirements.txt                 # pyspark, numpy
├── shared/
│   ├── parser.py                    # stop data parser (shared by lab2, lab3)
│   └── paths.py                     # data file paths
├── deliveryLogistics-lab1/          # Lab 1 — Hadoop MapReduce
│   ├── map.py
│   ├── red.py
│   ├── Sort.py
│   ├── Duom Full.zip                # main dataset (unzip before use)
│   └── Duom Cut.txt                 # smaller sample
├── deliveryLogistics-lab2/          # Lab 2 — Spark RDD
│   └── main.py
└── routeSummary-lab3/               # Lab 3 — Spark DataFrame + ML
    ├── main.py
    └── RouteSummary.txt
```
