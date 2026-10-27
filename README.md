# AI Data Analysis Assistant

An interactive data analysis application built with **Streamlit, Pandas,
Plotly, and the OpenAI API**. Upload a CSV or Excel dataset, explore its
contents, ask questions in natural language, generate visualizations,
inspect data quality, clean data, and create a downloadable PDF report.

## Features

-   **CSV and Excel upload** --- load datasets in `.csv` and `.xlsx`
    formats.
-   **Data explorer** --- preview records and inspect columns and data
    types.
-   **Automatic data cleaning** --- trim whitespace, remove duplicate
    rows, handle missing values using configurable strategies, and
    download the cleaned dataset.
-   **Cleaning summary** --- review the cleaning actions and the number
    of affected records.
-   **Ask your data** --- ask natural-language questions and use an
    OpenAI model to create a structured analysis plan.
-   **Computed results** --- perform supported operations such as row
    counts, missing-value checks, numeric summaries, unique-value
    counts, and grouped aggregations.
-   **Interactive charts** --- generate charts with Plotly, including
    bar charts, line charts, scatter plots, histograms, and pie charts
    where the selected data supports them.
-   **Automated EDA** --- inspect descriptive statistics, missing
    values, correlations, and potential outliers.
-   **AI-generated insights** --- request explanations of computed
    results and summaries of exploratory data analysis.
-   **PDF report** --- export a report containing dataset statistics,
    data-quality findings, AI insights, and supported visualizations.
-   **Download cleaned data** --- export the cleaned dataset as a CSV
    file.

> **Note:** Cleaning strategies and supported analysis operations depend
> on the dataset. Potential outliers are identified for review; they
> should not automatically be assumed to be errors.

## Tech Stack

-   **Python**
-   **Streamlit** --- web application interface
-   **Pandas and NumPy** --- data processing and numerical operations
-   **Plotly** --- interactive visualizations
-   **OpenAI API** --- natural-language analysis planning and
    AI-generated explanations
-   **ReportLab** --- PDF report generation
-   **python-dotenv** --- environment variable management
-   **openpyxl** --- Excel file support
-   **Kaleido** --- optional chart image export for PDF reports

## Project Structure

``` text
AI Data Analysis/
├── app.py
├── .env
├── .gitignore
├── requirements.txt
└── src/
    ├── __init__.py
    ├── analysis.py
    ├── ai_insights.py
    ├── data_cleaning.py
    └── pdf_report.py
```

The exact filenames may differ depending on your implementation.

## Prerequisites

-   Python installed on your computer
-   An OpenAI API key with access to the model configured in your
    project
-   Internet access for OpenAI API requests

## Installation and Setup

### 1. Clone or download the project

If the project is hosted on GitHub:

``` bash
git clone <your-repository-url>
cd <your-project-folder>
```

Alternatively, open your existing project folder in VS Code.

### 2. Create and activate a virtual environment (recommended)

**Windows Command Prompt:**

``` cmd
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies

``` cmd
python -m pip install -r requirements.txt
```

If you do not have a `requirements.txt` file yet, create one with the
dependencies used by the project:

``` text
streamlit
pandas
numpy
plotly
openai
python-dotenv
openpyxl
reportlab
kaleido
```

### 4. Configure the OpenAI API key

Create a `.env` file in the project root, alongside `app.py`:

``` dotenv
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=your_supported_model_id
```

Replace the example values with your API key and a model ID available to
your OpenAI API account. The application should read these values using
`python-dotenv`.

**Keep your API key private.** Do not upload `.env` to GitHub or share
it in screenshots, logs, or source code.

### 5. Start the application

From the project root, run:

``` cmd
streamlit run app.py
```

Streamlit will display a local address in the terminal. Open that
address in your browser.

## How to Use

1.  **Upload a dataset:** Select a CSV or Excel file.
2.  **Explore the data:** Review the preview, columns, and data types.
3.  **Clean the data:** Choose the available cleaning options, run the
    cleaning process, and inspect the cleaning summary and preview.
4.  **Use the cleaned dataset:** If the application provides an explicit
    option to use cleaned data, select it before running analysis.
5.  **Ask questions:** Enter a natural-language question, such as:
    -   `How many rows are in this dataset?`
    -   `What is the average salary?`
    -   `Show total sales by category.`
    -   `Which columns contain missing values?`
6.  **Explore EDA:** Review descriptive statistics, missing values,
    correlations, and potential outliers.
7.  **Generate a PDF report:** Create and download a report using the
    available reporting controls.
8.  **Download cleaned data:** Export the processed dataset when needed.

## Data Cleaning

The cleaning module can support the following actions, depending on the
configured options:

-   Remove completely empty rows
-   Remove exact duplicate rows
-   Trim leading and trailing whitespace from text values
-   Standardize column-name whitespace
-   Fill missing numeric values using the mean or median
-   Fill missing categorical values using the mode or an `"Unknown"`
    label
-   Leave missing values unchanged when selected
-   Show a summary of cleaning actions

Review the before-and-after data before using the result for important
decisions. Imputation changes the dataset and may affect statistical
conclusions. The initial implementation does not automatically remove
outliers.

## Natural-Language Analysis

The OpenAI API helps interpret a user's question and produce a
structured analysis plan. The application should validate the returned
plan and execute supported operations through Python and Pandas rather
than executing arbitrary model-generated code.

The model configured in `.env` must be available to your API account.
API requests require internet connectivity and may incur usage charges.

## PDF Reports

The PDF report module can include dataset-level statistics,
missing-value and outlier summaries, AI-generated EDA insights, and
chart images when chart export is configured.

If charts do not appear in the PDF, verify the Kaleido installation and
any browser/runtime requirements for the installed version.

## Security and Privacy

-   Keep `.env` and API credentials out of version control.
-   Add `.env`, virtual environments, caches, and private datasets to
    `.gitignore`.
-   Do not upload confidential or personally identifiable data unless
    you are authorized to process it through the configured services.
-   Review the data sent to the OpenAI API. Avoid sending unnecessary
    raw records or sensitive columns.
-   Validate uploaded files and model-generated analysis plans before
    processing them.

Example `.gitignore`:

``` gitignore
.env
.venv/
__pycache__/
*.py[cod]
.streamlit/
data/
```

Adjust the `data/` rule if your repository intentionally includes sample
datasets.

## Troubleshooting

### `OPENAI_API_KEY is missing`

-   Check that `.env` is in the project root, alongside `app.py`.
-   Confirm the variable is named `OPENAI_API_KEY`.
-   Restart Streamlit after changing environment variables.

### Model not found or unavailable

-   Set `OPENAI_MODEL` to a model ID available to your OpenAI API
    account.
-   Check API access, project permissions, and billing configuration.

### Unsupported `max_tokens` parameter

Some models require `max_completion_tokens` instead of `max_tokens` in
the Chat Completions request. Use the parameter supported by the model
and API endpoint you selected.

### Unsupported `temperature` value

Some models only accept the default temperature. If the API reports that
a custom temperature is unsupported, remove the `temperature` parameter
from the request.

### Invalid analysis plan

-   Inspect the raw model response in the development terminal.
-   Parse the JSON response defensively and handle Markdown code fences
    if present.
-   Validate operation names and column names against the uploaded
    dataset.
-   Make sure the analysis plan uses the schema expected by the
    application.

### Excel file cannot be read

Confirm that `openpyxl` is installed and that the uploaded file is a
supported `.xlsx` file.

### Charts missing from PDF

Check that Plotly and Kaleido are installed and compatible. The
interactive charts may work even when static image export for PDF
generation is not configured.

## Future Enhancements

Potential improvements include:

-   Before-and-after data-quality comparison
-   Reversible cleaning steps and cleaning history
-   Additional date and numeric type validation
-   Configurable outlier handling
-   Export cleaned data to Excel
-   More analysis operations and chart types
-   Downloadable EDA summaries and cleaning logs

## Author

**Adithyan S Anil**

AI/Data Science projects focused on Python, data analysis, machine
learning, and practical AI applications.

------------------------------------------------------------------------

*This README describes the intended capabilities and setup. Update the
project structure, model configuration, and feature descriptions to
match the exact implementation in your repository.*
