import time
import psutil
import os
import statistics


def measure_execution(func):

    process = psutil.Process(os.getpid())

    memory_before = (
        process.memory_info().rss
        / (1024 * 1024)
    )

    start_time = time.perf_counter()

    result = func()

    end_time = time.perf_counter()

    memory_after = (
        process.memory_info().rss
        / (1024 * 1024)
    )

    execution_time = (
        end_time - start_time
    )

    memory_used = (
        memory_after - memory_before
    )

    return {
        "execution_time": execution_time,
        "memory_used": memory_used,
        "result": result
    }


def benchmark_execution(
    func,
    runs=5,
    warmup_runs=1
):

    # --------------------------------------------------------
    # WARM-UP
    # --------------------------------------------------------

    for _ in range(warmup_runs):

        func()

    # --------------------------------------------------------
    # BENCHMARK RUNS
    # --------------------------------------------------------

    execution_times = []
    memory_values = []

    for _ in range(runs):

        process = psutil.Process(
            os.getpid()
        )

        memory_before = (
            process.memory_info().rss
            / (1024 * 1024)
        )

        start_time = time.perf_counter()

        func()

        end_time = time.perf_counter()

        memory_after = (
            process.memory_info().rss
            / (1024 * 1024)
        )

        execution_time = (
            end_time - start_time
        )

        memory_used = (
            memory_after - memory_before
        )

        execution_times.append(
            execution_time
        )

        memory_values.append(
            memory_used
        )

    # --------------------------------------------------------
    # STATISTICS
    # --------------------------------------------------------

    average_time = (
        statistics.mean(
            execution_times
        )
    )

    median_time = (
        statistics.median(
            execution_times
        )
    )

    minimum_time = min(
        execution_times
    )

    maximum_time = max(
        execution_times
    )

    average_memory = (
        statistics.mean(
            memory_values
        )
    )

    return {

        "runs": runs,

        "execution_times":
            execution_times,

        "average_time":
            average_time,

        "median_time":
            median_time,

        "minimum_time":
            minimum_time,

        "maximum_time":
            maximum_time,

        "average_memory":
            average_memory
    }