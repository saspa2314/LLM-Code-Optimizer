import ast
import re


def extract_code(response):
    """
    Extract Python code from an LLM response.

    If the response contains a Markdown code block, the code inside
    the block is returned. Otherwise, the original response is returned.
    """

    pattern = r"```(?:python|py)?\s*(.*?)```"
    match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)

    if match:
        return match.group(1).strip()

    return response.strip()


def validate_code(code):
    """
    Validate Python syntax.
    """

    try:
        ast.parse(code)
        return True, "Code is valid Python."

    except SyntaxError as e:
        return False, (
            f"Syntax error at line {e.lineno}, "
            f"column {e.offset}: {e.msg}"
        )


def clean_and_validate(response):
    """
    Extract code from an LLM response and validate it.
    """

    code = extract_code(response)
    valid, message = validate_code(code)

    return {
        "code": code,
        "valid": valid,
        "message": message
    }


def main():

    sample_response = """
Certainly! Here is the optimized code:

```python
numbers = [i * 2 for i in range(100000)]
print(numbers)
```

This version uses a list comprehension.
"""

    print("=" * 60)
    print("CODE EXTRACTION AND VALIDATION TEST")
    print("=" * 60)

    result = clean_and_validate(sample_response)

    print("\nExtracted Code:")
    print("-" * 60)
    print(result["code"])

    print("\nValidation:")
    print("-" * 60)
    print(result["message"])

    print("\nValid:", result["valid"])

    print("=" * 60)


if __name__ == "__main__":
    main()
