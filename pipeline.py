import os
import io
import contextlib

from llm.analyzer import analyze_code
from llm.optimizer import optimize_code

from utils.helpers import clean_and_validate

from execution.metrics import benchmark_execution
from execution.spark_runner import execute_spark_code


# ============================================================
# PYTHON EXECUTION
# ============================================================

def execute_python_code(code):

    output = io.StringIO()

    namespace = {}

    def run():

        output.seek(0)
        output.truncate(0)

        with contextlib.redirect_stdout(output):

            exec(
                code,
                namespace
            )

    try:

        benchmark_result = benchmark_execution(
            run,
            runs=5,
            warmup_runs=1
        )

        final_output = output.getvalue()

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

            "output":
                output.getvalue(),

            "error": str(e)
        }


# ============================================================
# GENERIC CODE EXECUTION
# ============================================================

def execute_code(
    code,
    language
):

    if language.lower() == "python":

        return execute_python_code(
            code
        )

    elif language.lower() == "pyspark":

        return execute_spark_code(
            code
        )

    else:

        return {

            "success": False,

            "execution_time": 0,

            "average_time": 0,

            "minimum_time": 0,

            "maximum_time": 0,

            "execution_times": [],

            "memory_used": 0,

            "output": "",

            "error":
                f"Unsupported language: {language}"
        }


# ============================================================
# COMPARE OUTPUTS
# ============================================================

def compare_outputs(
    original_output,
    optimized_output
):

    return (
        original_output.strip()
        ==
        optimized_output.strip()
    )



# ============================================================
# SAVE EXPERIMENT RESULT
# ============================================================

import csv
from pathlib import Path
from datetime import datetime


def save_llm_result(
    language,
    original_code,
    optimized_code,
    original_time,
    optimized_time,
    improvement,
    correctness,
    decision
):
    results_dir = Path(__file__).resolve().parent / "experiments"
    results_dir.mkdir(parents=True, exist_ok=True)

    file_path = results_dir / "llm_results.csv"

    # Consistent schema for Python and PySpark pipeline results.
    fieldnames = [
        "timestamp",
        "language",
        "original_code",
        "optimized_code",
        "original_time",
        "optimized_time",
        "improvement",
        "correctness",
        "decision",
    ]

    # Write the header for new or empty files.
    write_header = (
        not file_path.exists()
        or file_path.stat().st_size == 0
    )

    row = {
        "timestamp": datetime.now().isoformat(
            sep=" ", timespec="seconds"
        ),
        "language": language,
        "original_code": original_code,
        "optimized_code": optimized_code,
        "original_time": original_time,
        "optimized_time": optimized_time,
        "improvement": improvement,
        "correctness": correctness,
        "decision": decision,
    }

    with open(
        file_path,
        "a",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
            extrasaction="ignore",
        )

        if write_header:
            writer.writeheader()

        writer.writerow(row)


# ============================================================
# MAIN PIPELINE
# ============================================================

def run_pipeline(
    code,
    language="Python"
):

    print("=" * 70)
    print("LLM CODE OPTIMIZATION PIPELINE")
    print("=" * 70)

    print(
        f"\nLanguage: {language}"
    )


    # ========================================================
    # STEP 1 — ANALYSIS
    # ========================================================

    print(
        "\n[1/7] Analyzing original code..."
    )

    analysis = analyze_code(
        code
    )

    print(
        "Analysis completed."
    )


    # ========================================================
    # STEP 2 — OPTIMIZATION
    # ========================================================

    print(
        "\n[2/7] Generating optimized code..."
    )

    optimized_response = optimize_code(
        code,
        analysis
    )

    print(
        "Optimization generated."
    )


    # ========================================================
    # STEP 3 — EXTRACT CODE
    # ========================================================

    print(
        "\n[3/7] Extracting optimized code..."
    )

    extracted = clean_and_validate(
        optimized_response
    )

    optimized_code = extracted[
        "code"
    ]

    print(
        "Code extracted."
    )


    # ========================================================
    # STEP 4 — VALIDATE CODE
    # ========================================================

    print(
        "\n[4/7] Validating optimized code..."
    )

    if not extracted["valid"]:

        print(
            extracted["message"]
        )

        return {

            "success": False,

            "error":
                extracted["message"],

            "decision":
                "REJECT - INVALID CODE",

            "correctness":
                "FAIL",

            "original_time": 0,

            "optimized_time": 0,

            "improvement": 0,

            "optimized_code":
                optimized_code
        }

    print(
        extracted["message"]
    )


    # ========================================================
    # STEP 5 — ORIGINAL BENCHMARK
    # ========================================================

    print(
        "\n[5/7] Benchmarking original code..."
    )

    original_result = execute_code(
        code,
        language
    )

    if not original_result["success"]:

        print(
            "\nOriginal code execution failed."
        )

        print(
            original_result.get(
                "error",
                "Unknown error"
            )
        )

        return {

            "success": False,

            "error":
                original_result.get(
                    "error",
                    "Original execution failed"
                ),

            "decision":
                "REJECT - ORIGINAL EXECUTION FAILED",

            "correctness":
                "FAIL",

            "original_time": 0,

            "optimized_time": 0,

            "improvement": 0,

            "optimized_code":
                optimized_code
        }


    print(
        "\nOriginal benchmark:"
    )

    print(
        f"Median Time : "
        f"{original_result['execution_time']:.6f} seconds"
    )

    for i, value in enumerate(
        original_result[
            "execution_times"
        ],
        start=1
    ):

        print(
            f"Run {i}: "
            f"{value:.6f} seconds"
        )


    # ========================================================
    # STEP 6 — OPTIMIZED BENCHMARK
    # ========================================================

    print(
        "\n[6/7] Benchmarking optimized code..."
    )

    optimized_result = execute_code(
        optimized_code,
        language
    )


    # --------------------------------------------------------
    # OPTIMIZED EXECUTION FAILURE
    # --------------------------------------------------------

    if not optimized_result["success"]:

        print(
            "\nOptimized code execution failed."
        )

        print(
            optimized_result.get(
                "error",
                "Unknown optimized execution error"
            )
        )

        return {

            "success": False,

            "error":
                optimized_result.get(
                    "error",
                    "Optimized execution failed"
                ),

            "decision":
                "REJECT - OPTIMIZED EXECUTION FAILED",

            "correctness":
                "FAIL",

            "original_time":
                original_result[
                    "execution_time"
                ],

            "optimized_time": 0,

            "improvement": 0,

            "optimized_code":
                optimized_code
        }


    print(
        "\nOptimized benchmark:"
    )

    print(
        f"Median Time : "
        f"{optimized_result['execution_time']:.6f} seconds"
    )

    for i, value in enumerate(
        optimized_result[
            "execution_times"
        ],
        start=1
    ):

        print(
            f"Run {i}: "
            f"{value:.6f} seconds"
        )


    # ========================================================
    # STEP 7 — CORRECTNESS
    # ========================================================

    print(
        "\n[7/7] Checking output correctness..."
    )

    correctness = compare_outputs(
        original_result["output"],
        optimized_result["output"]
    )


    if correctness:

        print(
            "Outputs are identical."
        )

    else:

        print(
            "WARNING: Outputs are different."
        )


    # ========================================================
    # PERFORMANCE IMPROVEMENT
    # ========================================================

    original_time = (
        original_result[
            "execution_time"
        ]
    )

    optimized_time = (
        optimized_result[
            "execution_time"
        ]
    )


    if original_time > 0:

        improvement = (
            (
                original_time
                -
                optimized_time
            )
            /
            original_time
        ) * 100

    else:

        improvement = 0


    # ========================================================
    # DECISION ENGINE
    # ========================================================

    if not correctness:

        decision = (
            "REJECT - OUTPUT CHANGED"
        )

    elif optimized_time >= original_time:

        decision = (
            "REJECT - CORRECT BUT SLOWER"
        )

    elif improvement <= 0:

        decision = (
            "REJECT - NO PERFORMANCE BENEFIT"
        )

    else:

        decision = (
            "ACCEPT - CORRECT AND FASTER"
        )


    # ========================================================
    # FINAL RESULT
    # ========================================================

    print(
        "\n" + "=" * 70
    )

    print(
        "FINAL OPTIMIZATION RESULT"
    )

    print(
        "=" * 70
    )

    print(
        f"Original Median : "
        f"{original_time:.6f} seconds"
    )

    print(
        f"Optimized Median: "
        f"{optimized_time:.6f} seconds"
    )

    print(
        f"Improvement     : "
        f"{improvement:.2f}%"
    )

    print(
        f"Correctness     : "
        f"{'PASS' if correctness else 'FAIL'}"
    )

    print(
        f"Decision        : "
        f"{decision}"
    )

    print(
        "=" * 70
    )


    # ========================================================
    # SAVE RESULT
    # ========================================================

    save_llm_result(
        language,
        code,
        optimized_code,
        original_time,
        optimized_time,
        improvement,
        "PASS" if correctness else "FAIL",
        decision
    )


    return {

        "success": True,

        "analysis":
            analysis,

        "optimized_code":
            optimized_code,

        "original_time":
            original_time,

        "optimized_time":
            optimized_time,

        "improvement":
            improvement,

        "correctness":
            "PASS"
            if correctness
            else "FAIL",

        "decision":
            decision,

        "original_output":
            original_result["output"],

        "optimized_output":
            optimized_result["output"]
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    sample_code = """

numbers = []

for i in range(100000):

    numbers.append(
        i * 2
    )

print(
    sum(numbers)
)

"""

    result = run_pipeline(
        sample_code,
        language="Python"
    )

    print(
        "\nPipeline finished."
    )