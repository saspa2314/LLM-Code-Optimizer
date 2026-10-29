
import streamlit as st
import pandas as pd
from pathlib import Path
from pipeline import run_pipeline

# --------------------------------------------------
# Page configuration
# --------------------------------------------------
st.set_page_config(
    page_title="LLM Code Optimizer",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

RESULTS_FILE = Path("../LLM-Code-Optimizer/experiments/llm_results.csv")

# --------------------------------------------------
# Styling
# --------------------------------------------------
st.markdown(
    """
    <style>
        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 2rem;
        }
        .hero {
            padding: 1.3rem;
            border: 1px solid rgba(128,128,128,.3);
            border-radius: 14px;
            margin-bottom: 1rem;
        }
        .subtle {
            opacity: 0.75;
            font-size: 0.95rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# Helper functions
# --------------------------------------------------
def safe_float(value, default=0.0):
    try:
        value = float(value)
        return value if pd.notna(value) else default
    except (TypeError, ValueError):
        return default


def display_code(code, language):
    if code is None or not str(code).strip():
        st.code("# No code available", language="python")
    else:
        st.code(str(code), language=language.lower())


def load_history():
    if not RESULTS_FILE.exists():
        return pd.DataFrame()

    try:
        return pd.read_csv(RESULTS_FILE)
    except (pd.errors.EmptyDataError, OSError, ValueError):
        return pd.DataFrame()


# --------------------------------------------------
# Sidebar
# --------------------------------------------------
with st.sidebar:
    st.title("⚡ Code Optimizer")
    st.caption("LLM-powered performance optimization")

    st.divider()

    page = st.radio(
        "Navigation",
        ["Code Optimizer", "Experiment History"],
    )

    st.divider()

    st.markdown("### System information")
    st.write("**LLM:** Qwen2.5-Coder")
    st.write("**Backend:** Ollama")
    st.write("**Execution:** Local")
    st.write("**Languages:** Python / PySpark")

    st.divider()

    st.caption(
        "Generated optimizations are evaluated using "
        "execution and correctness checks provided by the pipeline."
    )


# ==================================================
# PAGE 1: CODE OPTIMIZER
# ==================================================
if page == "Code Optimizer":

    st.markdown(
        """
        <div class="hero">
            <h1 style="margin:0">LLM-Driven Code Optimization</h1>
            <p class="subtle">
                Analyze, optimize, validate, and benchmark your code
                using a locally running language model.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    language = st.selectbox(
        "Select programming language",
        ["Python", "PySpark"],
    )

    python_example = '''numbers = []

for i in range(100000):
    numbers.append(i * 2)

print(sum(numbers))
'''

    pyspark_example = '''from pyspark.sql import functions as F

data = (
    spark.range(100000)
    .withColumn("sales", (F.col("id") % 1000) + 100)
    .withColumn("category", F.col("id") % 4)
)

result = (
    data.filter(F.col("sales") > 500)
    .groupBy("category")
    .agg(F.sum("sales").alias("total_sales"))
)

result.show()
'''

    default_code = (
        pyspark_example if language == "PySpark"
        else python_example
    )

    # Keep editor content between Streamlit reruns.
    if "editor_language" not in st.session_state:
        st.session_state.editor_language = language
        st.session_state.source_code = default_code

    elif st.session_state.editor_language != language:
        st.session_state.editor_language = language
        st.session_state.source_code = default_code

    with st.expander("Load example code"):
        st.write("Load a sample program into the editor.")
        if st.button("Load example", use_container_width=True):
            st.session_state.source_code = default_code
            st.rerun()

    source_code = st.text_area(
        "Source code",
        key="source_code",
        height=330,
        placeholder="Paste your Python or PySpark code here...",
    )

    run_col, clear_col = st.columns([3, 1])

    with run_col:
        optimize_clicked = st.button(
            "🚀 Optimize and Benchmark",
            type="primary",
            use_container_width=True,
        )

    with clear_col:
        if st.button("Clear editor", use_container_width=True):
            st.session_state.source_code = ""
            st.session_state.pop("result", None)
            st.rerun()

    if optimize_clicked:

        if not source_code.strip():
            st.warning("Please enter some code first.")

        else:
            st.session_state.pop("result", None)

            try:
                with st.spinner(
                    "Running analysis, optimization, and benchmarks..."
                ):
                    result = run_pipeline(
                        source_code,
                        language=language,
                    )

                if not isinstance(result, dict):
                    raise TypeError(
                        "The pipeline did not return a dictionary."
                    )

                st.session_state.result = result
                st.session_state.result_source_code = source_code
                st.session_state.result_language = language

            except Exception as error:
                st.error(f"Pipeline error: {error}")

    # --------------------------------------------------
    # Display result
    # --------------------------------------------------
    result = st.session_state.get("result")

    if result:

        st.divider()
        st.header("Optimization Results")

        success = bool(result.get("success", False))

        validation_message = result.get(
            "validation_message",
            result.get(
                "decision",
                "The pipeline did not return a validation message.",
            ),
        )

        if success:
            st.success(str(validation_message))
        else:
            st.error(str(validation_message))

        decision = result.get("decision")
        if decision:
            st.markdown(f"**Decision:** {decision}")

        with st.expander("View code analysis", expanded=False):
            analysis = result.get("analysis")
            if analysis:
                st.write(str(analysis))
            else:
                st.info("No analysis was returned.")

        # Code comparison
        st.subheader("Code Comparison")

        original_code = result.get(
            "original_code",
            st.session_state.get(
                "result_source_code",
                source_code,
            ),
        )

        optimized_code = result.get("optimized_code", "")

        result_language = st.session_state.get(
            "result_language",
            language,
        )

        original_col, optimized_col = st.columns(2)

        with original_col:
            st.markdown("#### Original Code")
            display_code(original_code, result_language)

        with optimized_col:
            st.markdown("#### Optimized Code")
            display_code(optimized_code, result_language)

            if optimized_code:
                st.download_button(
                    "Download optimized code",
                    data=str(optimized_code),
                    file_name=(
                        "optimized_code.py"
                        if result_language == "Python"
                        else "optimized_spark_code.py"
                    ),
                    mime="text/x-python",
                    use_container_width=True,
                )

        # Performance metrics
        original_time_value = result.get("original_time")
        optimized_time_value = result.get("optimized_time")

        if (
            original_time_value is not None
            and optimized_time_value is not None
        ):
            original_time = safe_float(original_time_value)
            optimized_time = safe_float(optimized_time_value)

            if result.get("improvement") is not None:
                improvement = safe_float(result.get("improvement"))
            elif original_time > 0:
                improvement = (
                    (original_time - optimized_time)
                    / original_time
                ) * 100
            else:
                improvement = 0.0

            st.divider()
            st.subheader("Performance Benchmark")

            metric1, metric2, metric3 = st.columns(3)

            metric1.metric(
                "Original Runtime",
                f"{original_time:.6f} s",
            )

            metric2.metric(
                "Optimized Runtime",
                f"{optimized_time:.6f} s",
            )

            metric3.metric(
                "Runtime Improvement",
                f"{improvement:+.2f}%",
                help="Positive means faster; negative means slower.",
            )

            chart_data = pd.DataFrame(
                {
                    "Version": ["Original", "Optimized"],
                    "Execution Time (seconds)": [
                        original_time,
                        optimized_time,
                    ],
                }
            )

            st.markdown("#### Execution Time Comparison")
            st.bar_chart(
                chart_data.set_index("Version")
            )

            if success and improvement > 0:
                st.success(
                    f"Runtime decreased by {improvement:.2f}% "
                    "in this benchmark."
                )
            elif success and improvement < 0:
                st.warning(
                    f"Runtime increased by {abs(improvement):.2f}%. "
                    "The optimized version was slower in this run."
                )
            elif success:
                st.info("No runtime improvement was measured.")

        # Output comparison
        st.divider()
        st.subheader("Program Output")

        output_col1, output_col2 = st.columns(2)

        with output_col1:
            st.markdown("#### Original Output")
            original_output = result.get("original_output")
            st.code(
                str(original_output)
                if original_output is not None
                else "No output captured."
            )

        with output_col2:
            st.markdown("#### Optimized Output")
            optimized_output = result.get("optimized_output")
            st.code(
                str(optimized_output)
                if optimized_output is not None
                else "No output captured."
            )

        if not success:
            st.info(
                "This optimization was not accepted by the pipeline. "
                "Inspect the validation message and generated code "
                "before using it."
            )


# ==================================================
# PAGE 2: EXPERIMENT HISTORY
# ==================================================
else:

    st.title("📚 Experiment History")
    st.caption(
        "Review benchmark records saved by the optimization pipeline."
    )

    history = load_history()

    if history.empty:

        st.info(
            "No experiment history is available yet. "
            "Run an optimization first."
        )

    else:

        # Convert metric columns safely.
        for column in [
            "original_time",
            "optimized_time",
            "improvement",
        ]:
            if column in history.columns:
                history[column] = pd.to_numeric(
                    history[column],
                    errors="coerce",
                )

        # Summary metrics
        total_experiments = len(history)

        improvement_values = (
            history["improvement"].dropna()
            if "improvement" in history.columns
            else pd.Series(dtype=float)
        )

        average_improvement = (
            improvement_values.mean()
            if not improvement_values.empty
            else 0.0
        )

        best_improvement = (
            improvement_values.max()
            if not improvement_values.empty
            else 0.0
        )

        faster_runs = (
            int((improvement_values > 0).sum())
            if not improvement_values.empty
            else 0
        )

        m1, m2, m3, m4 = st.columns(4)

        m1.metric(
            "Recorded Experiments",
            total_experiments,
        )

        m2.metric(
            "Average Improvement",
            f"{average_improvement:+.2f}%",
        )

        m3.metric(
            "Best Improvement",
            f"{best_improvement:+.2f}%",
        )

        m4.metric(
            "Faster Runs",
            faster_runs,
        )

        # Runtime history chart
        if {
            "original_time",
            "optimized_time",
        }.issubset(history.columns):

            st.divider()
            st.subheader("Execution Time History")

            runtime_history = history[
                ["original_time", "optimized_time"]
            ].copy()

            runtime_history.columns = [
                "Original Runtime (s)",
                "Optimized Runtime (s)",
            ]

            st.line_chart(runtime_history)

        # Improvement chart
        if "improvement" in history.columns:

            st.subheader("Runtime Improvement History")

            improvement_chart = history[
                ["improvement"]
            ].rename(
                columns={
                    "improvement": "Improvement (%)",
                }
            )

            st.bar_chart(improvement_chart)

        # Full data table
        st.divider()
        st.subheader("All Experiment Records")

        st.dataframe(
            history,
            use_container_width=True,
            hide_index=True,
        )

        # Best recorded result
        if (
            "improvement" in history.columns
            and not improvement_values.empty
        ):

            best_index = history["improvement"].idxmax()
            best_row = history.loc[best_index]

            st.divider()
            st.subheader("🏆 Best Recorded Experiment")

            st.metric(
                "Recorded Improvement",
                f"{safe_float(best_row.get('improvement')):+.2f}%",
            )

            if (
                "original_time" in history.columns
                and pd.notna(best_row.get("original_time"))
            ):
                st.write(
                    "Original runtime: "
                    f"{safe_float(best_row.get('original_time')):.6f} s"
                )

            if (
                "optimized_time" in history.columns
                and pd.notna(best_row.get("optimized_time"))
            ):
                st.write(
                    "Optimized runtime: "
                    f"{safe_float(best_row.get('optimized_time')):.6f} s"
                )

            if "optimized_code" in history.columns:
                st.markdown("#### Best Recorded Optimized Code")
                display_code(
                    best_row.get("optimized_code", ""),
                    "Python",
                )


# --------------------------------------------------
# Footer
# --------------------------------------------------
st.divider()

st.caption(
    "LLM-Driven Code Optimization System | "
    "Ollama + Qwen2.5-Coder | "
    "Correctness Validation + Runtime Benchmarking"
)
