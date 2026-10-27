
import numpy as np
import pandas as pd


def get_eda_profile(df):
    numeric = df.select_dtypes(include=np.number)
    missing = df.isna().sum()

    profile = {
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
        "column_names": [str(c) for c in df.columns],
        "data_types": {
            str(c): str(df[c].dtype) for c in df.columns
        },
        "missing_values": {
            str(c): int(v) for c, v in missing.items() if v > 0
        },
        "missing_percentage": {
            str(c): round(float(v / max(len(df), 1) * 100), 2)
            for c, v in missing.items() if v > 0
        },
        "duplicate_rows": int(df.duplicated().sum()),
        "numeric_summary": numeric.describe().round(2).to_dict(),
        "categorical_columns": [
            str(c) for c in df.select_dtypes(
                include=["object", "category", "string"]
            ).columns
        ],
        "numeric_columns": [str(c) for c in numeric.columns]
    }

    outliers = {}

    for col in numeric.columns:
        series = numeric[col].dropna()

        if len(series) == 0:
            continue

        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1

        if iqr == 0:
            count = 0
        else:
            count = int(
                ((series < q1 - 1.5 * iqr) |
                 (series > q3 + 1.5 * iqr)).sum()
            )

        outliers[str(col)] = count

    profile["potential_outlier_counts_iqr"] = outliers

    if len(numeric.columns) >= 2:
        corr = numeric.corr().round(3)
        profile["correlations"] = corr.where(
            np.triu(np.ones(corr.shape), k=1).astype(bool)
        ).stack().to_dict()
        profile["correlations"] = {
            f"{a} vs {b}": float(v)
            for (a, b), v in profile["correlations"].items()
        }
    else:
        profile["correlations"] = {}

    return profile


def run_analysis(df, operation, column=None, group_by=None):
    if operation == "row_count":
        return {"row_count": int(len(df))}

    if operation == "column_names":
        return {"columns": [str(c) for c in df.columns]}

    if operation == "missing_values":
        return {
            str(c): int(v)
            for c, v in df.isna().sum().items()
        }

    if column not in df.columns:
        raise ValueError("Invalid or missing column.")

    if operation == "sum":
        if not pd.api.types.is_numeric_dtype(df[column]):
            raise ValueError("Sum requires a numerical column.")
        return {"sum": float(df[column].sum())}

    if operation == "mean":
        if not pd.api.types.is_numeric_dtype(df[column]):
            raise ValueError("Average requires a numerical column.")
        return {"mean": float(df[column].mean())}

    if operation == "maximum":
        return {"maximum": str(df[column].max())}

    if operation == "minimum":
        return {"minimum": str(df[column].min())}

    if operation == "unique_count":
        return {"unique_count": int(df[column].nunique())}

    if operation == "group_sum":
        if group_by not in df.columns:
            raise ValueError("Invalid grouping column.")
        if not pd.api.types.is_numeric_dtype(df[column]):
            raise ValueError("Grouped sum requires a numerical column.")

        result = (
            df.groupby(group_by, dropna=False, as_index=False)
            [column]
            .sum()
            .sort_values(column, ascending=False)
        )

        return result.head(50).to_dict(orient="records")

    if operation == "group_mean":
        if group_by not in df.columns:
            raise ValueError("Invalid grouping column.")
        if not pd.api.types.is_numeric_dtype(df[column]):
            raise ValueError("Grouped average requires a numerical column.")

        result = (
            df.groupby(group_by, dropna=False, as_index=False)
            [column]
            .mean()
            .sort_values(column, ascending=False)
        )

        return result.head(50).to_dict(orient="records")

    raise ValueError("Unsupported analysis operation.")


import plotly.express as px



def create_chart(df, plan):
    chart_type = plan.get("chart_type", "none")
    column = plan.get("column")
    group_by = plan.get("group_by")
    operation = plan.get("operation")

    if chart_type == "none":
        return None

    if chart_type == "histogram":
        if column not in df.columns:
            return None

        return px.histogram(
            df.dropna(subset=[column]),
            x=column,
            title=f"Distribution of {column}"
        )

    if chart_type == "scatter":
        if column not in df.columns or group_by not in df.columns:
            return None

        if column not in df.select_dtypes(include=np.number).columns:
            return None

        if group_by not in df.select_dtypes(include=np.number).columns:
            return None

        return px.scatter(
            df,
            x=column,
            y=group_by,
            title=f"{group_by} vs {column}"
        )

    if chart_type in {"bar", "line", "pie"}:
        if operation in {"group_sum", "group_mean"}:
            category = group_by
            measure = column
            aggregation = operation.replace("group_", "")
        else:
            category = column
            measure = group_by
            aggregation = "sum"

        if category not in df.columns or measure not in df.columns:
            return None

        if measure not in df.select_dtypes(include=np.number).columns:
            return None

        data = df[[category, measure]].dropna()

        if data.empty:
            return None

        grouped = data.groupby(
            category, as_index=False, dropna=False
        )[measure]

        if aggregation == "mean":
            grouped = grouped.mean()
        else:
            grouped = grouped.sum()

        grouped = grouped.sort_values(
            measure, ascending=False
        ).head(30)

        if chart_type == "bar":
            return px.bar(
                grouped,
                x=category,
                y=measure,
                title=f"{measure} by {category}"
            )

        if chart_type == "line":
            return px.line(
                grouped,
                x=category,
                y=measure,
                markers=True,
                title=f"{measure} by {category}"
            )

        return px.pie(
            grouped,
            names=category,
            values=measure,
            title=f"{measure} distribution"
        )

    return None