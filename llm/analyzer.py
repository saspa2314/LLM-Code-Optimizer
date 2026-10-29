import ollama


# Ollama model used for code analysis
MODEL = "qwen2.5-coder:3b"


def analyze_code(code):
    """
    Analyze Python or PySpark code using the local Ollama LLM.
    """

    prompt = f"""
You are an expert in Python, Pandas, and PySpark performance optimization.

Analyze the following code carefully.

Your task is to identify genuine performance and efficiency problems.

Check for:

1. Inefficient algorithms
2. Unnecessary loops
3. Repeated calculations
4. Inefficient data structures
5. Unnecessary memory usage
6. Inefficient Pandas operations
7. Inefficient PySpark operations
8. Unnecessary data movement
9. Poor Spark transformations
10. Opportunities for vectorization
11. Opportunities for list comprehensions
12. Opportunities for caching
13. Opportunities for reducing unnecessary columns
14. Python UDF usage in PySpark
15. Other potential performance bottlenecks

For every issue you find, provide:

- Problem
- Why it is inefficient
- Recommended optimization
- Expected performance benefit

IMPORTANT RULES:

- Do NOT blindly recommend threading.
- Do NOT blindly recommend multiprocessing.
- Do NOT recommend an optimization unless it is appropriate.
- Do not change the program's intended functionality.
- Prefer simple and reliable optimizations.
- If the code is already efficient, say so.
- Do not invent performance improvements without justification.

Return your answer in the following format:

## Analysis

### Issue 1

Problem:
...

Why:
...

Recommendation:
...

Expected Benefit:
...

### Issue 2

Problem:
...

Why:
...

Recommendation:
...

Expected Benefit:
...

## Overall Recommendation

...

Here is the code:

```python
{code}
```
"""

    try:
        response = ollama.chat(
            model=MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response["message"]["content"]

    except Exception as e:
        return f"Error while communicating with Ollama: {str(e)}"


def main():

    sample_code = """
numbers = []

for i in range(100000):
    numbers.append(i * 2)

print(numbers)
"""

    print("=" * 60)
    print("LLM CODE ANALYZER")
    print("=" * 60)

    print("\nAnalyzing code using Ollama...")
    print("Model:", MODEL)

    analysis = analyze_code(sample_code)

    print("\n" + "=" * 60)
    print("ANALYSIS RESULT")
    print("=" * 60)

    print(analysis)

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
