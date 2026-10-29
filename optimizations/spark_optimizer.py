import os
import sys
import time
import csv

# --------------------------------------------------
# Force PySpark to use the current Python interpreter
# --------------------------------------------------

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable


from pyspark.sql import SparkSession
from pyspark.sql.functions import col, upper, when


# --------------------------------------------------
# Create Spark session
# --------------------------------------------------

def create_spark():

    spark = (
        SparkSession.builder
        .appName("LLM-Code-Optimizer")
        .master("local[*]")
        .config("spark.pyspark.python", sys.executable)
        .config("spark.pyspark.driver.python", sys.executable)
        .getOrCreate()
    )

    spark.sparkContext.setLogLevel("ERROR")

    return spark


# --------------------------------------------------
# Measure execution time
# --------------------------------------------------

def measure_time(function):

    start = time.perf_counter()

    result = function()

    end = time.perf_counter()

    return end - start, result


# ==================================================
# TEST 1
# Unnecessary Columns → Column Selection
# ==================================================

def column_optimization(spark):

    print("\n========== TEST 1: COLUMN OPTIMIZATION ==========")

    data = [
        (
            i,
            f"User_{i}",
            i % 60,
            i * 100,
            i % 2,
            f"City_{i % 10}"
        )
        for i in range(1, 100001)
    ]

    columns = [
        "id",
        "name",
        "age",
        "salary",
        "active",
        "city"
    ]

    df = spark.createDataFrame(data, columns)

    # Original version
    def original():

        result = (
            df
            .filter(col("salary") > 500000)
            .select(
                "id",
                "name",
                "age",
                "salary",
                "active",
                "city"
            )
        )

        return result.count()

    # Optimized version
    def optimized():

        result = (
            df
            .select("id", "salary")
            .filter(col("salary") > 500000)
        )

        return result.count()

    original_time, original_result = measure_time(original)

    optimized_time, optimized_result = measure_time(optimized)

    improvement = (
        (original_time - optimized_time)
        / original_time
    ) * 100

    print(f"Original Time  : {original_time:.6f} seconds")
    print(f"Optimized Time : {optimized_time:.6f} seconds")
    print(f"Improvement    : {improvement:.2f}%")

    return {
        "test": "Column Selection",
        "original_time": original_time,
        "optimized_time": optimized_time,
        "improvement": improvement
    }


# ==================================================
# TEST 2
# Python UDF → Spark Built-in Function
# ==================================================

def udf_optimization(spark):

    print("\n========== TEST 2: UDF OPTIMIZATION ==========")

    data = [
        (i, f"user_{i}")
        for i in range(1, 100001)
    ]

    columns = ["id", "name"]

    df = spark.createDataFrame(data, columns)

    # ------------------------------------------------
    # Original version
    # Python function executed through UDF
    # ------------------------------------------------

    from pyspark.sql.functions import udf
    from pyspark.sql.types import StringType

    def convert_upper(value):

        return value.upper()

    upper_udf = udf(
        convert_upper,
        StringType()
    )

    def original():

        result = df.withColumn(
            "upper_name",
            upper_udf(col("name"))
        )

        return result.count()

    # ------------------------------------------------
    # Optimized version
    # Spark built-in function
    # ------------------------------------------------

    def optimized():

        result = df.withColumn(
            "upper_name",
            upper(col("name"))
        )

        return result.count()

    original_time, original_result = measure_time(original)

    optimized_time, optimized_result = measure_time(optimized)

    improvement = (
        (original_time - optimized_time)
        / original_time
    ) * 100

    print(f"Original Time  : {original_time:.6f} seconds")
    print(f"Optimized Time : {optimized_time:.6f} seconds")
    print(f"Improvement    : {improvement:.2f}%")

    return {
        "test": "Python UDF to Spark Built-in",
        "original_time": original_time,
        "optimized_time": optimized_time,
        "improvement": improvement
    }


# ==================================================
# TEST 3
# Repeated Calculation → Reuse Cached DataFrame
# ==================================================

def caching_optimization(spark):

    print("\n========== TEST 3: CACHING OPTIMIZATION ==========")

    data = [
        (
            i,
            i % 60,
            i * 100
        )
        for i in range(1, 100001)
    ]

    columns = [
        "id",
        "age",
        "salary"
    ]

    df = spark.createDataFrame(data, columns)

    # ------------------------------------------------
    # Original version
    # Same filtered DataFrame is calculated twice
    # ------------------------------------------------

    def original():

        filtered = df.filter(
            col("salary") > 500000
        )

        count1 = filtered.count()

        count2 = filtered.filter(
            col("age") > 30
        ).count()

        return count1 + count2

    # ------------------------------------------------
    # Optimized version
    # Cache the intermediate result
    # ------------------------------------------------

    def optimized():

        filtered = (
            df
            .filter(col("salary") > 500000)
            .cache()
        )

        count1 = filtered.count()

        count2 = filtered.filter(
            col("age") > 30
        ).count()

        filtered.unpersist()

        return count1 + count2

    original_time, original_result = measure_time(original)

    optimized_time, optimized_result = measure_time(optimized)

    improvement = (
        (original_time - optimized_time)
        / original_time
    ) * 100

    print(f"Original Time  : {original_time:.6f} seconds")
    print(f"Optimized Time : {optimized_time:.6f} seconds")
    print(f"Improvement    : {improvement:.2f}%")

    return {
        "test": "Caching Repeated Data",
        "original_time": original_time,
        "optimized_time": optimized_time,
        "improvement": improvement
    }


# ==================================================
# Save Results
# ==================================================

def save_results(results):

    os.makedirs(
        "experiments",
        exist_ok=True
    )

    file_path = os.path.join(
        "experiments",
        "spark_results.csv"
    )

    with open(
        file_path,
        "w",
        newline=""
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "Test",
            "Original Time",
            "Optimized Time",
            "Improvement (%)"
        ])

        for result in results:

            writer.writerow([
                result["test"],
                f"{result['original_time']:.6f}",
                f"{result['optimized_time']:.6f}",
                f"{result['improvement']:.2f}"
            ])

    print("\nSpark results saved to:")
    print(file_path)


# ==================================================
# Main
# ==================================================

def main():

    print("\n==========================================")
    print("   PySpark Code Optimization Experiments")
    print("==========================================")

    spark = create_spark()

    print("\nSpark started successfully!")

    results = []

    print("\nRunning Test 1...")

    results.append(
        column_optimization(spark)
    )

    print("\nRunning Test 2...")

    results.append(
        udf_optimization(spark)
    )

    print("\nRunning Test 3...")

    results.append(
        caching_optimization(spark)
    )

    save_results(results)

    spark.stop()

    print("\n==========================================")
    print("All Spark experiments completed!")
    print("==========================================")


# ==================================================
# Run program
# ==================================================

if __name__ == "__main__":

    main()