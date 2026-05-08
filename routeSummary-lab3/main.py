import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.regression import LinearRegression
from shared.parser import parse_line
from shared.paths import STOPS_DATA, ROUTE_SUMMARY


def laikas_to_minutes(t):
    t = t.strip('"')
    h, m = t.split(':')
    return int(h) * 60 + int(m)


def main():
    spark = SparkSession.builder.appName('Lab3-Task4').getOrCreate()
    spark.sparkContext.setLogLevel('ERROR')

    stops_rdd = spark.sparkContext.textFile(STOPS_DATA).flatMap(parse_line)
    stops_df = spark.createDataFrame(
        stops_rdd.filter(
            lambda s: s.get('marsrutas') and s.get('sustojimo data')
                      and s.get('Masinos tipas') and s.get('svoris')
        ).map(lambda s: (s['marsrutas'], s['sustojimo data'], s['Masinos tipas'], float(s['svoris']))),
        ['marsrutas', 'sustojimo_data', 'Masinos_tipas', 'svoris']
    )

    single_vehicle = (
        stops_df
        .groupBy('marsrutas', 'sustojimo_data')
        .agg(F.countDistinct('Masinos_tipas').alias('n_vehicles'))
        .filter(F.col('n_vehicles') == 1)
    )

    svoris_agg = (
        stops_df
        .groupBy('marsrutas', 'sustojimo_data')
        .agg(F.sum('svoris').alias('svoris_sum'))
        .join(single_vehicle, on=['marsrutas', 'sustojimo_data'])
        .select('marsrutas', 'sustojimo_data', 'svoris_sum')
    )

    laikas_udf = F.udf(laikas_to_minutes)
    summary = (
        spark.read.csv(ROUTE_SUMMARY, header=True, inferSchema=False)
        .select(
            F.col('marsrutas').cast('string'),
            F.col('sustojimo data').alias('sustojimo_data'),
            F.col('BendrasLaikas')
        )
        .withColumn('laikas_min', laikas_udf(F.col('BendrasLaikas')).cast('double'))
    )

    joined = svoris_agg.join(summary, on=['marsrutas', 'sustojimo_data']).dropna()

    assembler = VectorAssembler(inputCols=['svoris_sum'], outputCol='features')
    ml_data = assembler.transform(joined).select('features', F.col('laikas_min').alias('label'))

    model = LinearRegression(featuresCol='features', labelCol='label').fit(ml_data)

    print('\n=== Task 4: BendrasLaikas ~ svoris_sum (single Masinos tipas routes) ===')
    print(f'  Intercept  (b0): {model.intercept:.4f} minutes')
    print(f'  Coefficient (b1): {model.coefficients[0]:.6f} minutes per kg')
    print(f'  RMSE:             {model.summary.rootMeanSquaredError:.4f}')
    print(f'  R²:               {model.summary.r2:.4f}')
    print(f'  Training samples: {model.summary.numInstances:.0f}')
    print(f'\n  BendrasLaikas = {model.intercept:.2f} + {model.coefficients[0]:.6f} * svoris_sum')

    spark.stop()


if __name__ == '__main__':
    main()
