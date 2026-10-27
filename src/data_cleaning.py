
import pandas as pd
import numpy as np


def clean_dataset(
    df,
    numeric_strategy="median",
    categorical_strategy="mode",
    remove_duplicates=True,
    standardize_text=True
):
    cleaned = df.copy()
    report = []

    # Remove completely empty rows
    empty_rows = int(cleaned.isna().all(axis=1).sum())

    if empty_rows:
        cleaned = cleaned.dropna(how="all")
        report.append({
            "Action": "Remove empty rows",
            "Affected": empty_rows
        })

    # Standardize text values and column names
    if standardize_text:
        cleaned.columns = [
            str(col).strip() for col in cleaned.columns
        ]

        for col in cleaned.select_dtypes(
            include=["object", "string"]
        ).columns:
            cleaned[col] = cleaned[col].map(
                lambda value: value.strip()
                if isinstance(value, str) else value
            )

            cleaned[col] = cleaned[col].replace(
                r"^\s*$", np.nan, regex=True
            )

    # Remove duplicate rows
    if remove_duplicates:
        duplicates = int(cleaned.duplicated().sum())

        if duplicates:
            cleaned = cleaned.drop_duplicates()
            report.append({
                "Action": "Remove duplicate rows",
                "Affected": duplicates
            })

    # Fill missing values
    for col in cleaned.columns:
        missing = int(cleaned[col].isna().sum())

        if missing == 0:
            continue

        if pd.api.types.is_numeric_dtype(cleaned[col]):
            if numeric_strategy == "median":
                fill_value = cleaned[col].median()
            elif numeric_strategy == "mean":
                fill_value = cleaned[col].mean()
            else:
                fill_value = None

        else:
            if categorical_strategy == "mode":
                modes = cleaned[col].mode(dropna=True)
                fill_value = modes.iloc[0] if not modes.empty else None
            elif categorical_strategy == "unknown":
                fill_value = "Unknown"
            else:
                fill_value = None

        if fill_value is not None and not pd.isna(fill_value):
            cleaned[col] = cleaned[col].fillna(fill_value)

            report.append({
                "Action": f"Fill missing values in {col}",
                "Affected": missing
            })

    summary = pd.DataFrame(
        report,
        columns=["Action", "Affected"]
    )

    return cleaned, summary
