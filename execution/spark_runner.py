import os
import sys
import io
from contextlib import redirect_stdout

from pyspark.sql import SparkSession

from execution.metrics import benchmark_execution


# ============================================================
# PYSPARK CONFIGURATION
# ============================================================

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable


# ============================================================
# CREATE SPARK SESSION
# ============================================================

def create_spark_session():

    spark = (
        SparkSession.builder
        .appName("LLM-Code-Optimizer")
        .master("local[*]")
        .config(
            "spark.pyspark.python",
            sys.executable
        )
        .config(
            "spark.pyspark.driver.python",
            sys.executable
        )
        .config(
            "spark.ui.enabled",
            "false"
        )
        .getOrCreate()
    )

    spark.sparkContext.setLogLevel(
        "ERROR"
    )

    return spark


# ============================================================
# EXECUTE PYSPARK CODE
# ============================================================

def execute_spark_code(code):

    spark = create_spark_session()

    try:

        def run():

            # Clear Spark cache from previous benchmark run
            spark.catalog.clearCache()

            # Fresh namespace for every execution
            namespace = {
                "spark": spark
            }

            output = io.StringIO()

            with redirect_stdout(output):

                exec(
                    code,
                    namespace
                )

            return output.getvalue()

        # ----------------------------------------------------
        # BENCHMARK
        # ----------------------------------------------------

        benchmark_result = benchmark_execution(
            run,
            runs=5,
            warmup_runs=1
        )

        # ----------------------------------------------------
        # FINAL OUTPUT
        # ----------------------------------------------------

        final_output = run()

        return {

            "success": True,

            "execution_time":
                benchmark_result["median_time"],

            "average_time":
                benchmark_result["average_time"],

            "minimum_time":
                benchmark_result["minimum_time"],

            "maximum_time":
                benchmark_result["maximum_time"],

            "execution_times":
                benchmark_result["execution_times"],

            "memory_used":
                benchmark_result["average_memory"],

            "output":
                final_output
        }

    except Exception as e:

        return {

            "success": False,

            "execution_time": 0,

            "average_time": 0,

            "minimum_time": 0,

            "maximum_time": 0,

            "execution_times": [],

            "memory_used": 0,

            "output": "",

            "error": str(e)
        }

    finally:

        spark.stop()
# ============================================================
# TEST
# ============================================================

def main():

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

    print("=" * 70)
    print("PYSPARK MULTI-RUN BENCHMARK")
    print("=" * 70)

    result = execute_spark_code(
        sample_code
    )

    if result["success"]:

        print(
            "\nIndividual Runs:"
        )

        for i, value in enumerate(
            result["execution_times"],
            start=1
        ):

            print(
                f"Run {i}: "
                f"{value:.6f} seconds"
            )

        print(
            "\nStatistics:"
        )

        print(
            f"Average : "
            f"{result['average_time']:.6f} seconds"
        )

        print(
            f"Median  : "
            f"{result['execution_time']:.6f} seconds"
        )

        print(
            f"Minimum : "
            f"{result['minimum_time']:.6f} seconds"
        )

        print(
            f"Maximum : "
            f"{result['maximum_time']:.6f} seconds"
        )

        print(
            f"Memory  : "
            f"{result['memory_used']:.2f} MB"
        )

        print(
            "\nOutput:"
        )

        print(
            result["output"]
        )

    else:

        print(
            "\nPySpark execution failed."
        )

        print(
            "Error:",
            result["error"]
        )

    print(
        "=" * 70
    )


if __name__ == "__main__":

    main()