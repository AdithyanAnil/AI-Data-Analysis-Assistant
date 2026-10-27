
import json
import os
import re

from dotenv import load_dotenv
from groq import Groq
from openai import OpenAI
load_dotenv()

MODEL = os.getenv("OPENAI_MODEL", "gpt-6-luna")


def get_client():
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY is missing from your .env file."
        )

    return OpenAI(api_key=api_key)



def ask_llm(system_prompt, user_prompt, max_tokens=800):
    client = get_client()

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        
        max_completion_tokens=max_tokens
    )

    content = response.choices[0].message.content

    if not content:
        raise ValueError("Openai returned an empty response.")

    return content



def create_analysis_plan(question, columns, numeric_columns):
    import json
    import re

    system_prompt = """
You are a data analysis planner.
Return ONLY one valid JSON object.
Do not include markdown, explanations, or code fences.

The JSON must contain exactly these keys:
operation, column, group_by, chart_type, explanation

Allowed operations:
row_count, column_names, missing_values, sum, mean,
maximum, minimum, unique_count, group_sum, group_mean

Allowed chart types:
bar, line, scatter, histogram, pie, none

Rules:
- For sum, mean, maximum, minimum, unique_count:
  column must be a valid dataset column.
- For group_sum and group_mean:
  column must be a numeric column.
  group_by must be a categorical or other grouping column.
- For histogram:
  column must be a numeric column.
- For scatter:
  column and group_by must both be numeric columns.
- For bar, line and pie:
  column must be the category column.
  group_by must be the numeric measure column.
- For row_count, column_names and missing_values:
  column and group_by must be null when not needed.
- If no chart is appropriate, use chart_type "none".

Example:
{"operation":"mean","column":"Sales","group_by":null,"chart_type":"none","explanation":"Calculate average sales"}
"""

    user_prompt = f"""
Question: {question}

Dataset columns: {json.dumps(list(columns))}
Numeric columns: {json.dumps(list(numeric_columns))}

Return the JSON analysis plan now.
"""

    try:
        response = ask_llm(
            system_prompt,
            user_prompt,
            max_tokens=500
        )

        print("RAW GROQ RESPONSE:", repr(response))

        if not response or not response.strip():
            raise ValueError("Groq returned an empty response.")

        # Remove Markdown code fences if present
        cleaned = response.strip()
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)

        # Extract the JSON object
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)

        if not match:
            raise ValueError(
                f"No JSON object found in Groq response: {cleaned}"
            )

        plan = json.loads(match.group(0))

        allowed_operations = {
            "row_count", "column_names", "missing_values",
            "sum", "mean", "maximum", "minimum",
            "unique_count", "group_sum", "group_mean"
        }

        allowed_charts = {
            "bar", "line", "scatter",
            "histogram", "pie", "none"
        }

        if plan.get("operation") not in allowed_operations:
            raise ValueError(
                f"Invalid operation: {plan.get('operation')}"
            )

        if plan.get("chart_type") not in allowed_charts:
            plan["chart_type"] = "none"

        # Validate column names against the uploaded dataset
        column = plan.get("column")
        group_by = plan.get("group_by")

        if column is not None and column not in columns:
            raise ValueError(
                f"Column '{column}' does not exist in the dataset."
            )

        if group_by is not None and group_by not in columns:
            raise ValueError(
                f"Grouping column '{group_by}' does not exist in the dataset."
            )

        operation = plan["operation"]

        if operation in {"sum", "mean", "maximum", "minimum", "group_sum", "group_mean"}:
            if column not in numeric_columns:
                raise ValueError(
                    f"Operation '{operation}' requires a numeric column."
                )

        if operation in {"group_sum", "group_mean"} and group_by is None:
            raise ValueError("Grouped operations require a group_by column.")

        if plan["chart_type"] == "histogram":
            if column not in numeric_columns:
                plan["chart_type"] = "none"

        if plan["chart_type"] == "scatter":
            if column not in numeric_columns or group_by not in numeric_columns:
                plan["chart_type"] = "none"

        if plan["chart_type"] in {"bar", "line", "pie"}:
            if operation in {"group_sum", "group_mean"}:
                if group_by is None or column not in numeric_columns:
                    plan["chart_type"] = "none"
            elif column is None or group_by not in numeric_columns:
                plan["chart_type"] = "none"

        return plan

    except Exception as e:
        print("ANALYSIS PLAN ERROR:", repr(e))
        raise ValueError(
            f"Could not create a valid analysis plan: {e}"
        ) from e

def explain_result(question, result):
    return ask_llm(
        """
You are a data analyst.
Explain the supplied computed result clearly.
Use only the supplied result and question.
Do not invent statistics, correlations, or causal explanations.
Mention when the result is insufficient to answer the question.
""",
        f"Question: {question}\nComputed result: {json.dumps(result, default=str)}",
        max_tokens=500
    )


def generate_eda_insights(profile):
    return ask_llm(
        """
You are a senior data analyst.
Write a structured exploratory data analysis report.
Cover data quality, distributions, potential outliers, correlations,
and suggested next steps.
Clearly distinguish facts from hypotheses.
Do not claim causation or invent missing results.
Use headings and concise bullet points.
""",
        f"Dataset profile:\n{json.dumps(profile, default=str)}",
        max_tokens=1200
    )