from pyspark.sql import SparkSession
from pyspark.sql import functions as F

from pipeline import run_pipeline


def create_spark_session():
    """Create or reuse the Spark session for benchmark dataset setup."""
    return (
        SparkSession.builder
        .appName("Spark LLM Benchmark")
        .master("local[*]")
        .config("spark.ui.enabled", "false")
        .getOrCreate()
    )
def create_dataset(spark):
    """Create a deterministic 100,000-row dataset for the tests."""
    return (
        spark.range(100000)
        .withColumn("customer_id", F.col("id"))
        .withColumn(
            "category",
            F.when(F.col("id") % 4 == 0, "Electronics")
            .when(F.col("id") % 4 == 1, "Clothing")
            .when(F.col("id") % 4 == 2, "Food")
            .otherwise("Furniture")
        )
        .withColumn("sales", (F.col("id") % 1000) + 100)
        .withColumn("quantity", (F.col("id") % 10) + 1)
        .withColumn("price", (F.col("id") % 500) + 50)
        .withColumn(
            "region",
            F.when(F.col("id") % 4 == 0, "South")
            .when(F.col("id") % 4 == 1, "North")
            .when(F.col("id") % 4 == 2, "East")
            .otherwise("West")
        )
    )
def build_setup_code():
    """Create the DataFrame inside the namespace used by the Spark runner."""
    return '''
from pyspark.sql import functions as F

data = (
    spark.range(100000)
    .withColumn("customer_id", F.col("id"))
    .withColumn(
        "category",
        F.when(F.col("id") % 4 == 0, "Electronics")
        .when(F.col("id") % 4 == 1, "Clothing")
        .when(F.col("id") % 4 == 2, "Food")
        .otherwise("Furniture")
    )
    .withColumn("sales", (F.col("id") % 1000) + 100)
    .withColumn("quantity", (F.col("id") % 10) + 1)
    .withColumn("price", (F.col("id") % 500) + 50)
    .withColumn(
        "region",
        F.when(F.col("id") % 4 == 0, "South")
        .when(F.col("id") % 4 == 1, "North")
        .when(F.col("id") % 4 == 2, "East")
        .otherwise("West")
    )
)
'''
def is_correct_result(result):
    """Normalize bool and string correctness values returned by the pipeline."""
    value = result.get("correctness", False)
    return value is True or str(value).strip().upper() in {
        "PASS", "TRUE", "CORRECT"
    }


def get_timing(result, *keys):
    """Read the first available timing key without assuming a specific schema."""
    for key in keys:
        value = result.get(key)
        if value is not None:
            return value
    return "N/A"

def run_test(spark, test_name, code):
    print("\n" + "=" * 70)
    print(test_name)
    print("=" * 70)

    # `data` must exist inside the fresh namespace created by spark_runner.py.
    full_code = build_setup_code() + "\n\n" + code
    result = run_pipeline(code=full_code, language="PySpark")

    original_time = get_timing(
        result,
        "original_median_time",
        "original_time",
        "original_execution_time"
    )
    optimized_time = get_timing(
        result,
        "optimized_median_time",
        "optimized_time",
        "optimized_execution_time"
    )
    improvement = result.get("improvement", "N/A")
    correct = is_correct_result(result)
    decision = str(result.get("decision", "N/A"))

    print("\nOriginal Median Time:")
    print(original_time)
    print("\nOptimized Median Time:")
    print(optimized_time)
    print("\nImprovement:")
    print(improvement)
    print("\nCorrectness:")
    print("PASS" if correct else "FAIL")
    print("\nDecision:")
    print(decision)

    if (
        not correct
        or "FAILED" in decision.upper()
        or "OUTPUT CHANGED" in decision.upper()
        or "INVALID" in decision.upper()
    ):
        print("\n" + "-" * 70)
        print("OPTIMIZED CODE")
        print("-" * 70)
        print(result.get("optimized_code", "No optimized code available."))

    # Preserve pipeline fields and attach normalized fields for summary reporting.
    result["_benchmark_correct"] = correct
    result["_benchmark_original_time"] = original_time
    result["_benchmark_optimized_time"] = optimized_time
    return result
def main():
    spark = create_spark_session()

    try:
        print("\n" + "=" * 70)
        print("AUTOMATED PYSPARK LLM BENCHMARK")
        print("=" * 70)

        # Setup check. The dataset is recreated inside each pipeline execution,
        # because spark_runner.py uses a fresh execution namespace.
        data = create_dataset(spark)
        data.createOrReplaceTempView("benchmark_data")
        print("\nDataset prepared: 100,000 rows.")

        test1_code = """
from pyspark.sql import functions as F

result = (
    data
    .select(
        "customer_id",
        "category",
        "sales",
        "region"
    )
)

result.show()
"""
        result1 = run_test(spark, "TEST 1: COLUMN SELECTION", test1_code)
        test2_code = """
from pyspark.sql import functions as F

result = (
    data
    .filter(F.col("sales") > 500)
    .groupBy("category")
    .agg(
        F.sum("sales").alias("total_sales"),
        F.avg("price").alias("average_price")
    )
)

result.show()
"""
        result2 = run_test(spark, "TEST 2: FILTER + AGGREGATION", test2_code)

        test3_code = """
from pyspark.sql import functions as F

filtered = data.filter(F.col("sales") > 500)
count_result = filtered.count()
sum_result = (
    filtered
    .agg(F.sum("sales").alias("total_sales"))
    .collect()[0][0]
)
print("Count:", count_result)
print("Sum:", sum_result)
"""
        result3 = run_test(spark, "TEST 3: REPEATED DATAFRAME USAGE", test3_code)

        results = [
            ("Column Selection", result1),
            ("Filter Aggregation", result2),
            ("Repeated DataFrame", result3),
        ]

        accepted = 0
        slower = 0
        failed = 0
        changed = 0
        other_rejected = 0

        print("\n" + "=" * 90)
        print("FINAL BENCHMARK SUMMARY")
        print("=" * 90)
        print(f"{'Test':<30}{'Correct':<12}{'Improvement':<16}{'Decision'}")
        print("-" * 90)
        for name, result in results:
            correctness = result.get("_benchmark_correct", False)
            improvement = result.get("improvement", "N/A")
            decision = str(result.get("decision", "UNKNOWN"))
            decision_upper = decision.upper()

            print(
                f"{name:<30}"
                f"{'PASS' if correctness else 'FAIL':<12}"
                f"{str(improvement):<16}"
                f"{decision}"
            )

            if decision_upper == "ACCEPT - CORRECT AND FASTER":
                accepted += 1
            elif "CORRECT BUT SLOWER" in decision_upper:
                slower += 1
            elif "OUTPUT CHANGED" in decision_upper:
                changed += 1
            elif "FAILED" in decision_upper or "INVALID" in decision_upper:
                failed += 1
            else:
                other_rejected += 1

        print("\nAccepted                  :", accepted)
        print("Correct but slower        :", slower)
        print("Output changed            :", changed)
        print("Runtime/validation failures:", failed)
        print("Other rejected/undetermined:", other_rejected)
        print("\n" + "=" * 90)
        print("BENCHMARK COMPLETE")
        print("=" * 90)

    finally:
        spark.stop()


if __name__ == "__main__":
    main()
