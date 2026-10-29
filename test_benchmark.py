from execution.metrics import benchmark_execution


def test_function():

    total = 0

    for i in range(100000):

        total += i

    return total


result = benchmark_execution(
    test_function,
    runs=5,
    warmup_runs=1
)


print("=" * 70)
print("BENCHMARK TEST")
print("=" * 70)

print("\nIndividual Runs:")

for i, value in enumerate(
    result["execution_times"],
    start=1
):

    print(
        f"Run {i}: "
        f"{value:.6f} seconds"
    )

print("\nStatistics:")

print(
    f"Average : "
    f"{result['average_time']:.6f} seconds"
)

print(
    f"Median  : "
    f"{result['median_time']:.6f} seconds"
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
    f"{result['average_memory']:.2f} MB"
)

print("=" * 70)