from metrics import measure_execution


def inefficient_code():

    numbers = list(range(1_000_000))

    result = []

    for number in numbers:
        if number % 2 == 0:
            result.append(number * 2)

    return result


def optimized_code():

    numbers = list(range(1_000_000))

    result = [number * 2 for number in numbers if number % 2 == 0]

    return result


# Measure inefficient code
original = measure_execution(inefficient_code)

# Measure optimized code
optimized = measure_execution(optimized_code)


print("\n===== ORIGINAL CODE =====")
print("Execution Time:", original["execution_time"], "seconds")
print("Memory Used:", original["memory_used"], "MB")


print("\n===== OPTIMIZED CODE =====")
print("Execution Time:", optimized["execution_time"], "seconds")
print("Memory Used:", optimized["memory_used"], "MB")


# Calculate improvement

time_improvement = (
    (original["execution_time"] - optimized["execution_time"])
    / original["execution_time"]
) * 100


print("\n===== PERFORMANCE IMPROVEMENT =====")
print("Execution Time Improvement:", time_improvement, "%")