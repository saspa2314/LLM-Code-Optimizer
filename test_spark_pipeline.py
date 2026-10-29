from pipeline import run_pipeline


sample_code = """
data = [
    ("Alice", 100),
    ("Bob", 200),
    ("Charlie", 300),
    ("David", 400)
]

df = spark.createDataFrame(
    data,
    ["name", "sales"]
)

result = df.filter(
    df.sales > 150
)

result.show()
"""


result = run_pipeline(
    sample_code,
    language="PySpark"
)


print("\n" + "=" * 70)
print("PYSPARK PIPELINE RESULT")
print("=" * 70)


if result["success"]:

    print("\nOptimized Code:")
    print("-" * 70)

    print(
        result["optimized_code"]
    )

    print("\nOriginal Time:")
    print(
        f"{result['original_time']:.6f} seconds"
    )

    print("\nOptimized Time:")
    print(
        f"{result['optimized_time']:.6f} seconds"
    )

    print("\nImprovement:")
    print(
        f"{result['improvement']:.2f}%"
    )

else:

    print("\nPipeline failed.")

    print(
        result.get(
            "error",
            "Unknown error"
        )
    )