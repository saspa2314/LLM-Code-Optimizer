
import ollama


MODEL = "qwen2.5-coder:3b"


def optimize_code(code, analysis):
    prompt = f"""
You are a senior Python and PySpark performance engineer.

Optimize the supplied code ONLY if a safe, technically justified
performance improvement exists. Preserve the exact behavior and results.

ABSOLUTE RULES

1. Preserve program semantics and exact results.
2. Never modify, replace, remove, truncate, sample, or recreate input data.
3. Never recreate an existing DataFrame.
4. Do not rewrite dataset/setup code, including spark.range(),
   createDataFrame(), withColumn(), file reads, SQL, or input lists.
5. Optimize only the target operation. Keep unrelated code unchanged.
6. Never create a new SparkSession or SparkContext.
7. Never add limit(), head(), take(), or first() unless present in
   the original code. These can change behavior.
8. Never remove rows or add filtering, sampling, or deduplication.
9. Preserve show() behavior. Never change result.show() to
   result.limit(20).show().
10. Preserve actions such as show(), count(), collect(), write(),
    first(), and take() unless equivalence is guaranteed.
11. Preserve output schema, column names, values, and row meaning.
12. Preserve filters, aggregations, joins, grouping, and ordering.
13. Use Spark Column expressions correctly; never use a Spark Column
    as a Python boolean.
14. Do not apply NumPy functions to Spark Column objects.
15. Do not convert Spark DataFrames to Pandas using toPandas().
16. Prefer Spark built-in functions over unnecessary Python UDFs.
17. Cache/persist only when a DataFrame is reused and caching is likely
    to help. Do not add caching to a DataFrame used only once.
18. Keep existing variable names and avoid unnecessary new variables.
19. Make the smallest possible change. Do not rewrite the whole program.
20. Do not change code merely to shorten it or reformat it.
21. Do not introduce approximations or early termination.
22. A simple DataFrame select() may already be optimized by Spark Catalyst.
    Do not invent an optimization when none exists.
23. If no safe optimization exists, return the original code unchanged.
24. Correctness is more important than speed. If uncertain, return the
    original code unchanged.
25. Do not add comments claiming an optimization unless it is real.
26. Do not change printed output or other observable behavior.
27. Do not modify the input/setup portion of the program.
28. Never add .limit() to make show() appear faster.
29. Never remove required transformations or aggregations.
30. Return complete executable Python code, not a partial snippet.

ORIGINAL CODE:
```python
{code}
```

CODE ANALYSIS:
{analysis}

FINAL REQUIREMENTS:
- Return the safest optimized version.
- Do not recreate input DataFrames or rewrite dataset creation.
- Do not create a new SparkSession.
- Do not add limit() or reduce the dataset.
- Do not change output, schema, filters, aggregations, joins, or actions.
- Make the smallest possible modification.
- If no safe optimization exists, return the ORIGINAL CODE unchanged.
- Return ONLY complete Python code inside exactly ONE Python code block.
- Do not provide explanations outside the code block.
ADDITIONAL PYSPARK SAFETY RULES:

1. Never use F.lit() with a Python dictionary, list, or mapping.
2. Never use a Python dictionary as a Spark SQL expression.
3. For conditional category or region mappings, use chained
   F.when(...).otherwise(...) expressions when appropriate.
4. Preserve the original DataFrame construction and all input columns.
5. Do not recreate or simplify the input dataset in a way that changes
   its values, schema, or behavior.
6. Preserve the original program's output and side effects.
7. If no safe optimization is identified, return the original code
   unchanged instead of inventing an optimization.
8. Only propose optimizations that can be validated by execution
   and output comparison.
9. Never use display(). Use the same output action as the original code.
10. Never put F.col(), F.when(), or other PySpark Column expressions
    inside selectExpr(). Use select() with Column expressions instead.
11. Copy the original input/setup code exactly, including spark.range(),
    DataFrame construction, and input column definitions.
12. Never replace the original dataset with a newly constructed dataset.
13. Preserve the original output actions and their results.
14. If an optimization requires rewriting the dataset or is uncertain,
    return the original code unchanged.
15. Never use Spark Column expressions as Python dictionary keys.
16. Never create Python dictionaries to map values in a Spark DataFrame.
17. Use Spark-native F.when() expressions for conditional mappings,
    or preserve the original transformation unchanged.
18. Do not generate lookup dictionaries for values derived from
    spark.range() or other DataFrame columns.
"""

    try:
        response = ollama.chat(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
        return response["message"]["content"]
    except Exception as exc:
        return f"Error while communicating with Ollama: {exc}"


def main():
    code = """
numbers = []

for i in range(100000):
    numbers.append(i * 2)

print(numbers)
"""
    analysis = """
The loop repeatedly appends values to a list.
A list comprehension may be faster and more concise.
"""
    optimized = optimize_code(code, analysis)

    print("=" * 60)
    print("OPTIMIZED CODE")
    print("=" * 60)
    print(optimized)


if __name__ == "__main__":
    main()
