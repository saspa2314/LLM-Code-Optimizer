import time

from pyspark.sql import functions as F

from execution.spark_runner import create_spark_session


# ============================================================
# CREATE SPARK SESSION
# ============================================================

spark = create_spark_session()


# ============================================================
# CREATE LARGE DATASET
# ============================================================

print("=" * 70)
print("CREATING PYSPARK BENCHMARK DATASET")
print("=" * 70)

start = time.perf_counter()

data = (
    spark.range(100000)
    .withColumn(
        "customer_id",
        F.col("id")
    )
    .withColumn(
        "category",
        F.when(
            (F.col("id") % 4) == 0,
            "Electronics"
        )
        .when(
            (F.col("id") % 4) == 1,
            "Clothing"
        )
        .when(
            (F.col("id") % 4) == 2,
            "Food"
        )
        .otherwise(
            "Furniture"
        )
    )
    .withColumn(
        "sales",
        (F.col("id") % 1000) + 100
    )
    .withColumn(
        "quantity",
        (F.col("id") % 10) + 1
    )
    .withColumn(
        "price",
        (F.col("id") % 500) + 50
    )
    .withColumn(
        "region",
        F.when(
            (F.col("id") % 4) == 0,
            "South"
        )
        .when(
            (F.col("id") % 4) == 1,
            "North"
        )
        .when(
            (F.col("id") % 4) == 2,
            "East"
        )
        .otherwise(
            "West"
        )
    )
)

# Force dataset creation
row_count = data.count()

end = time.perf_counter()


print(
    f"\nRows created: {row_count:,}"
)

print(
    f"Creation time: "
    f"{end - start:.4f} seconds"
)


# ============================================================
# SHOW DATASET STRUCTURE
# ============================================================

print("\nSchema:")
data.printSchema()


print("\nSample:")
data.show(5)


# ============================================================
# TEST 1
# UNNECESSARY COLUMNS
# ============================================================

print("=" * 70)
print("TEST 1: UNNECESSARY COLUMN SELECTION")
print("=" * 70)

original_1 = (
    data
    .select("*")
    .filter(
        F.col("sales") > 500
    )
)

optimized_1 = (
    data
    .select(
        "customer_id",
        "category",
        "sales"
    )
    .filter(
        F.col("sales") > 500
    )
)


print("\nOriginal:")
original_1.explain()


print("\nOptimized:")
optimized_1.explain()


print("\nOriginal count:")

start = time.perf_counter()

count_original = original_1.count()

original_time = (
    time.perf_counter() - start
)


print(
    f"Rows: {count_original:,}"
)

print(
    f"Time: {original_time:.6f} seconds"
)


print("\nOptimized count:")

start = time.perf_counter()

count_optimized = optimized_1.count()

optimized_time = (
    time.perf_counter() - start
)


print(
    f"Rows: {count_optimized:,}"
)

print(
    f"Time: {optimized_time:.6f} seconds"
)


improvement = (
    (original_time - optimized_time)
    / original_time
) * 100


print(
    f"\nImprovement: "
    f"{improvement:.2f}%"
)


# ============================================================
# TEST 2
# FILTER + AGGREGATION
# ============================================================

print("=" * 70)
print("TEST 2: FILTER AND AGGREGATION")
print("=" * 70)


original_2 = (
    data
    .filter(
        F.col("sales") > 500
    )
    .groupBy("category")
    .agg(
        F.sum("sales").alias(
            "total_sales"
        ),
        F.avg("price").alias(
            "average_price"
        )
    )
)


optimized_2 = (
    data
    .select(
        "category",
        "sales",
        "price"
    )
    .filter(
        F.col("sales") > 500
    )
    .groupBy("category")
    .agg(
        F.sum("sales").alias(
            "total_sales"
        ),
        F.avg("price").alias(
            "average_price"
        )
    )
)


print("\nOriginal:")

start = time.perf_counter()

result_original = original_2.collect()

original_time = (
    time.perf_counter() - start
)


print(
    f"Time: {original_time:.6f} seconds"
)


print("\nOptimized:")

start = time.perf_counter()

result_optimized = optimized_2.collect()

optimized_time = (
    time.perf_counter() - start
)


print(
    f"Time: {optimized_time:.6f} seconds"
)


improvement = (
    (original_time - optimized_time)
    / original_time
) * 100


print(
    f"\nImprovement: "
    f"{improvement:.2f}%"
)


print(
    "\nResults identical:",
    result_original == result_optimized
)


# ============================================================
# TEST 3
# REPEATED DATAFRAME USAGE
# ============================================================

print("=" * 70)
print("TEST 3: REPEATED DATAFRAME USAGE")
print("=" * 70)


filtered = (
    data
    .filter(
        F.col("sales") > 500
    )
)


print("\nWithout caching:")

start = time.perf_counter()

count_1 = filtered.count()

sum_1 = (
    filtered
    .agg(
        F.sum("sales")
    )
    .collect()
)


time_without_cache = (
    time.perf_counter() - start
)


print(
    f"Time: "
    f"{time_without_cache:.6f} seconds"
)


print("\nWith caching:")

cached = filtered.cache()

# Materialize cache
cached.count()

start = time.perf_counter()

count_2 = cached.count()

sum_2 = (
    cached
    .agg(
        F.sum("sales")
    )
    .collect()
)


time_with_cache = (
    time.perf_counter() - start
)


print(
    f"Time: "
    f"{time_with_cache:.6f} seconds"
)


improvement = (
    (time_without_cache - time_with_cache)
    / time_without_cache
) * 100


print(
    f"\nImprovement: "
    f"{improvement:.2f}%"
)


print(
    "\nCounts identical:",
    count_1 == count_2
)


# ============================================================
# CLEANUP
# ============================================================

cached.unpersist()

spark.stop()


print("\n" + "=" * 70)
print("SPARK BENCHMARK TEST COMPLETED")
print("=" * 70)
