import time
import csv
import os


# -----------------------------------------
# Measure execution time
# -----------------------------------------

def measure_time(function):

    start = time.perf_counter()

    result = function()

    end = time.perf_counter()

    return end - start, result


# -----------------------------------------
# Test 1: Loop → List Comprehension
# -----------------------------------------

def loop_optimization():

    numbers = list(range(1, 1000001))

    # Original version
    def original():

        result = []

        for number in numbers:

            if number % 2 == 0:
                result.append(number * 2)

        return result

    # Optimized version
    def optimized():

        return [
            number * 2
            for number in numbers
            if number % 2 == 0
        ]

    original_time, original_result = measure_time(original)
    optimized_time, optimized_result = measure_time(optimized)

    improvement = (
        (original_time - optimized_time)
        / original_time
    ) * 100

    print("\n========== TEST 1: LOOP OPTIMIZATION ==========")

    print(f"Original Time  : {original_time:.6f} seconds")
    print(f"Optimized Time : {optimized_time:.6f} seconds")
    print(f"Improvement    : {improvement:.2f}%")

    return {
        "test": "Loop to List Comprehension",
        "original_time": original_time,
        "optimized_time": optimized_time,
        "improvement": improvement
    }


# -----------------------------------------
# Test 2: String Concatenation → Join
# -----------------------------------------

def string_optimization():

    words = ["Python"] * 100000

    # Original version
    def original():

        result = ""

        for word in words:

            result += word

        return result

    # Optimized version
    def optimized():

        return "".join(words)

    original_time, original_result = measure_time(original)
    optimized_time, optimized_result = measure_time(optimized)

    improvement = (
        (original_time - optimized_time)
        / original_time
    ) * 100

    print("\n========== TEST 2: STRING OPTIMIZATION ==========")

    print(f"Original Time  : {original_time:.6f} seconds")
    print(f"Optimized Time : {optimized_time:.6f} seconds")
    print(f"Improvement    : {improvement:.2f}%")

    return {
        "test": "String Concatenation to Join",
        "original_time": original_time,
        "optimized_time": optimized_time,
        "improvement": improvement
    }


# -----------------------------------------
# Test 3: Nested Loop → Set Lookup
# -----------------------------------------

def search_optimization():

    data = list(range(100000))
    search_values = list(range(50000, 150000))

    # Original version
    def original():

        result = []

        for value in search_values:

            for item in data:

                if value == item:

                    result.append(value)
                    break

        return result

    # Optimized version
    def optimized():

        data_set = set(data)

        return [
            value
            for value in search_values
            if value in data_set
        ]

    original_time, original_result = measure_time(original)
    optimized_time, optimized_result = measure_time(optimized)

    improvement = (
        (original_time - optimized_time)
        / original_time
    ) * 100

    print("\n========== TEST 3: SEARCH OPTIMIZATION ==========")

    print(f"Original Time  : {original_time:.6f} seconds")
    print(f"Optimized Time : {optimized_time:.6f} seconds")
    print(f"Improvement    : {improvement:.2f}%")

    return {
        "test": "Nested Loop to Set Lookup",
        "original_time": original_time,
        "optimized_time": optimized_time,
        "improvement": improvement
    }


# -----------------------------------------
# Save results to CSV
# -----------------------------------------

def save_results(results):

    folder = "experiments"

    os.makedirs(folder, exist_ok=True)

    file_path = os.path.join(
        folder,
        "results.csv"
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
                result["original_time"],
                result["optimized_time"],
                result["improvement"]
            ])

    print("\nResults saved to:")
    print(file_path)


# -----------------------------------------
# Main program
# -----------------------------------------

def main():

    print("\n========================================")
    print("   Python Code Optimization Experiments")
    print("========================================")

    results = []

    results.append(
        loop_optimization()
    )

    results.append(
        string_optimization()
    )

    results.append(
        search_optimization()
    )

    save_results(results)

    print("\n========================================")
    print("All Python experiments completed!")
    print("========================================")


if __name__ == "__main__":
    main()