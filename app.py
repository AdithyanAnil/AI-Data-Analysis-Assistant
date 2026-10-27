import streamlit as st
import pandas as pd
import numpy as np
from src.data_cleaning import clean_dataset

from src.analysis import (
    get_eda_profile,
    run_analysis,
    create_chart
)
from src.ai_insights import (
    create_analysis_plan,
    explain_result,
    generate_eda_insights
)
from src.pdf_report import create_pdf_report


st.set_page_config(
    page_title="AI Data Analysis Assistant",
    page_icon=":material/insights:",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ---------------------------------------------------------------------------
# Design system (UI only - no logic changes)
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=DM+Sans:wght@400;500;600&display=swap');

    :root {
        --bg: #0d1117;
        --surface: #151b23;
        --surface-2: #1c2430;
        --border: #263040;
        --text: #e6edf3;
        --muted: #8b98a9;
        --accent: #2dd4bf;
        --accent-2: #f59e0b;
        --danger: #f87171;
        --radius: 14px;
    }

    html, body, [class*="css"], .stApp {
        font-family: 'DM Sans', sans-serif;
    }
    .stApp {
        background:
            radial-gradient(1200px 500px at 10% -10%, rgba(45,212,191,0.10), transparent 60%),
            radial-gradient(900px 400px at 100% 0%, rgba(245,158,11,0.07), transparent 60%),
            var(--bg);
        color: var(--text);
    }
    h1, h2, h3, h4 {
        font-family: 'Space Grotesk', sans-serif !important;
        letter-spacing: -0.02em;
        color: var(--text) !important;
    }
    .block-container { padding-top: 2rem; padding-bottom: 4rem; max-width: 1320px; }

    /* Hero */
    .hero {
        border: 1px solid var(--border);
        background: linear-gradient(135deg, rgba(45,212,191,0.12), rgba(21,27,35,0.9) 55%);
        border-radius: 20px;
        padding: 28px 32px;
        margin-bottom: 22px;
        animation: fadeUp .6s ease both;
    }
    .hero .eyebrow {
        text-transform: uppercase; letter-spacing: .18em;
        font-size: 11px; color: var(--accent); font-weight: 600;
    }
    .hero h1 { font-size: 2.3rem; margin: 6px 0 6px 0; padding: 0; }
    .hero p { color: var(--muted); margin: 0; font-size: 1rem; }

    /* Section header */
    .section {
        display: flex; align-items: center; gap: 12px;
        margin: 8px 0 14px 0;
    }
    .section .bar { width: 4px; height: 22px; border-radius: 4px; background: var(--accent); }
    .section h3 { margin: 0; font-size: 1.2rem; }
    .section-sub { color: var(--muted); font-size: .92rem; margin: -6px 0 16px 16px; }

    /* Metrics */
    [data-testid="stMetric"] {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 18px 20px;
        transition: transform .2s ease, border-color .2s ease, box-shadow .2s ease;
        animation: fadeUp .5s ease both;
    }
    [data-testid="stMetric"]:hover {
        transform: translateY(-3px);
        border-color: var(--accent);
        box-shadow: 0 10px 30px -12px rgba(45,212,191,0.45);
    }
    [data-testid="stMetricLabel"] p {
        color: var(--muted) !important; text-transform: uppercase;
        letter-spacing: .1em; font-size: 11px !important;
    }
    [data-testid="stMetricValue"] {
        font-family: 'Space Grotesk', sans-serif; color: var(--text);
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px; background: var(--surface);
        border: 1px solid var(--border); border-radius: 12px; padding: 6px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 42px; border-radius: 8px; padding: 0 18px;
        color: var(--muted); font-weight: 500; background: transparent;
        transition: background .2s ease, color .2s ease;
    }
    .stTabs [data-baseweb="tab"]:hover { color: var(--text); background: var(--surface-2); }
    .stTabs [aria-selected="true"] {
        background: var(--accent) !important; color: #06201c !important;
    }
    .stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] { display: none; }
    .stTabs [data-baseweb="tab-panel"] { padding-top: 22px; animation: fadeUp .4s ease both; }

    /* Buttons */
    .stButton > button, .stDownloadButton > button {
        border-radius: 10px; border: 1px solid var(--border);
        background: var(--surface-2); color: var(--text);
        font-weight: 600; padding: .55rem 1.1rem;
        transition: all .18s ease;
    }
    .stButton > button:hover, .stDownloadButton > button:hover {
        border-color: var(--accent); color: var(--accent);
        transform: translateY(-1px);
    }
    .stButton > button[kind="primary"] {
        background: var(--accent); color: #06201c; border-color: var(--accent);
    }
    .stButton > button[kind="primary"]:hover {
        filter: brightness(1.08); color: #06201c;
        box-shadow: 0 8px 24px -10px rgba(45,212,191,0.7);
    }

    /* Containers / cards */
    [data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: var(--radius) !important;
        border-color: var(--border) !important;
        background: rgba(21,27,35,0.6);
    }
    [data-testid="stDataFrame"] {
        border: 1px solid var(--border); border-radius: 12px; overflow: hidden;
    }
    [data-testid="stExpander"] {
        border: 1px solid var(--border); border-radius: 12px; background: var(--surface);
    }

    /* Inputs */
    [data-baseweb="select"] > div, .stTextInput input {
        background: var(--surface-2) !important; border-color: var(--border) !important;
        border-radius: 10px !important;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: var(--surface); border-right: 1px solid var(--border);
    }
    [data-testid="stFileUploaderDropzone"] {
        background: var(--surface-2); border: 1.5px dashed var(--border);
        border-radius: 12px; transition: border-color .2s ease;
    }
    [data-testid="stFileUploaderDropzone"]:hover { border-color: var(--accent); }
    .side-brand {
        font-family: 'Space Grotesk', sans-serif; font-weight: 700;
        font-size: 1.15rem; color: var(--text); margin-bottom: 2px;
    }
    .side-sub { color: var(--muted); font-size: .85rem; margin-bottom: 14px; }
    .pill {
        display: inline-block; padding: 3px 10px; border-radius: 999px;
        font-size: 11px; font-weight: 600; letter-spacing: .05em;
        border: 1px solid var(--border); color: var(--muted);
    }
    .pill.on { color: #06201c; background: var(--accent); border-color: var(--accent); }

    /* Chat */
    [data-testid="stChatMessage"] {
        background: var(--surface); border: 1px solid var(--border);
        border-radius: 14px; padding: 12px 16px; animation: fadeUp .35s ease both;
    }

    /* Empty state */
    .empty {
        border: 1.5px dashed var(--border); border-radius: 20px;
        padding: 60px 30px; text-align: center; background: var(--surface);
    }
    .empty h2 { margin-bottom: 8px; }
    .empty p { color: var(--muted); max-width: 520px; margin: 0 auto; }
    .steps { display: flex; gap: 14px; justify-content: center; margin-top: 26px; flex-wrap: wrap; }
    .step {
        background: var(--surface-2); border: 1px solid var(--border);
        border-radius: 12px; padding: 14px 18px; min-width: 180px; text-align: left;
        transition: transform .2s ease, border-color .2s ease;
    }
    .step:hover { transform: translateY(-3px); border-color: var(--accent); }
    .step b { color: var(--accent); font-family: 'Space Grotesk', sans-serif; }
    .step span { display: block; color: var(--muted); font-size: .85rem; margin-top: 4px; }

    @keyframes fadeUp {
        from { opacity: 0; transform: translateY(8px); }
        to { opacity: 1; transform: translateY(0); }
    }
    #MainMenu, footer { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True
)


def section(title, subtitle=None):
    st.markdown(
        f'<div class="section"><div class="bar"></div><h3>{title}</h3></div>',
        unsafe_allow_html=True
    )
    if subtitle:
        st.markdown(f'<div class="section-sub">{subtitle}</div>', unsafe_allow_html=True)


st.markdown(
    """
    <div class="hero">
        <div class="eyebrow">Analytics Workspace</div>
        <h1>AI Data Analysis Assistant</h1>
        <p>Explore data, ask questions, visualize patterns, and generate reports using AI.</p>
    </div>
    """,
    unsafe_allow_html=True
)

st.sidebar.markdown(
    '<div class="side-brand">Data Source</div>'
    '<div class="side-sub">Upload a CSV or Excel file to start your analysis.</div>',
    unsafe_allow_html=True
)

uploaded_file = st.sidebar.file_uploader(
    "Upload CSV or Excel",
    type=["csv", "xlsx"]
)

if uploaded_file is None:
    st.markdown(
        """
        <div class="empty">
            <h2>Upload a dataset to begin</h2>
            <p>Use the panel on the left to add a CSV or Excel file.
            The workspace will unlock exploration, cleaning, chat and reporting tools.</p>
            <div class="steps">
                <div class="step"><b>01 Upload</b><span>CSV or XLSX file</span></div>
                <div class="step"><b>02 Clean</b><span>Fix gaps and duplicates</span></div>
                <div class="step"><b>03 Ask</b><span>Query in plain language</span></div>
                <div class="step"><b>04 Report</b><span>Export a PDF summary</span></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.stop()

try:
    if uploaded_file.name.lower().endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    if df.empty:
        st.error("The uploaded dataset is empty.")
        st.stop()
        # Preserve the original uploaded dataset
    original_df = df.copy()

    # Select the dataset used by the analysis tabs
    if (
        st.session_state.get("use_cleaned_data", False)
        and "cleaned_df" in st.session_state
    ):
        df = st.session_state["cleaned_df"]
    else:
        df = original_df

    # Calculate the EDA profile using the active dataset
    profile = get_eda_profile(df)

    if not df.columns.is_unique:
        st.error(
            "Your dataset contains duplicate column names. "
            "Rename them to unique names before analysis."
        )
        st.stop()

except Exception as e:
    st.error(f"Unable to read the dataset: {e}")
    st.stop()

numeric_columns = df.select_dtypes(
    include=np.number
).columns.tolist()

profile = get_eda_profile(df)

# Sidebar status
_active = st.session_state.get("use_cleaned_data", False) and "cleaned_df" in st.session_state
st.sidebar.markdown(
    f'<div style="margin-top:6px">'
    f'<span class="pill {"on" if _active else ""}">'
    f'{"CLEANED DATA ACTIVE" if _active else "ORIGINAL DATA ACTIVE"}</span></div>',
    unsafe_allow_html=True
)
st.sidebar.caption(f"File: {uploaded_file.name}")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Rows", f"{len(df):,}")
c2.metric("Columns", f"{len(df.columns):,}")
c3.metric("Missing cells", f"{int(df.isna().sum().sum()):,}")
c4.metric("Duplicate rows", f"{int(df.duplicated().sum()):,}")

st.write("")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Data Explorer",
    "Data Cleaning",
    "Ask Your Data",
    "Automated EDA",
    "PDF Report"
])

with tab1:
    section("Dataset Preview", "First 100 rows of the active dataset.")
    st.dataframe(df.head(100), use_container_width=True, height=360)

    column_info = pd.DataFrame({
        "Column": df.columns.astype(str),
        "Data Type": df.dtypes.astype(str).values,
        "Missing Values": df.isna().sum().values,
        "Unique Values": df.nunique().values
    })

    with st.expander("Column Information", expanded=False):
        st.dataframe(column_info, use_container_width=True)

    st.write("")
    section("Automatic Chart Builder", "Pick a chart type and columns, then generate.")

    if numeric_columns:
        with st.container(border=True):
            cc1, cc2, cc3 = st.columns(3)

            with cc1:
                chart_type = st.selectbox(
                    "Chart type",
                    ["bar", "line", "scatter", "histogram", "pie"],
                    key="manual_chart_type"
                )

            with cc2:
                x_col = st.selectbox(
                    "Category or X-axis",
                    df.columns.tolist(),
                    key="manual_x"
                )

            with cc3:
                y_col = st.selectbox(
                    "Numerical column",
                    numeric_columns,
                    key="manual_y"
                )

            generate_clicked = st.button("Generate Chart", type="primary")

        if generate_clicked:
            try:
                if chart_type == "histogram":
                    fig = create_chart(df, {
                        "chart_type": "histogram",
                        "column": y_col
                    })

                elif chart_type == "scatter":
                    if x_col not in numeric_columns:
                        st.warning(
                            "Scatter plots require a numerical X-axis."
                        )
                        fig = None
                    else:
                        fig = create_chart(df, {
                            "chart_type": "scatter",
                            "column": x_col,
                            "group_by": y_col
                        })

                else:
                    fig = create_chart(df, {
                        "chart_type": chart_type,
                        "column": x_col,
                        "group_by": y_col
                    })

                if fig is not None:
                    st.session_state["latest_chart"] = fig
                    with st.container(border=True):
                        st.plotly_chart(fig, use_container_width=True)
                    st.toast("Chart generated and saved for the report.")

            except Exception as e:
                st.error(f"Chart generation failed: {e}")

    else:
        st.info("No numerical columns were found.")



with tab2:
    section("Automatic Data Cleaning", "Review the data-quality issues before applying cleaning.")

    with st.container(border=True):
        s1, s2 = st.columns(2)

        with s1:
            numeric_strategy = st.selectbox(
                "Missing numerical values",
                ["median", "mean", "leave unchanged"]
            )

        with s2:
            categorical_strategy = st.selectbox(
                "Missing categorical values",
                ["mode", "unknown", "leave unchanged"]
            )

        t1, t2 = st.columns(2)

        with t1:
            remove_duplicates = st.toggle(
                "Remove duplicate rows",
                value=True
            )

        with t2:
            standardize_text = st.toggle(
                "Trim whitespace and standardize column names",
                value=True
            )

        clean_clicked = st.button("Clean Dataset", type="primary")

    if clean_clicked:
        with st.spinner("Cleaning dataset..."):
            cleaned_df, cleaning_report = clean_dataset(
                df,
                numeric_strategy=numeric_strategy,
                categorical_strategy=categorical_strategy,
                remove_duplicates=remove_duplicates,
                standardize_text=standardize_text
            )

        st.session_state["cleaned_df"] = cleaned_df
        st.session_state["cleaning_report"] = cleaning_report

    if "cleaned_df" in st.session_state:
        cleaned_df = st.session_state["cleaned_df"]

        st.success("Cleaning process completed.")

        r1, r2, r3 = st.columns(3)
        r1.metric("Rows after cleaning", f"{len(cleaned_df):,}",
                  delta=f"{len(cleaned_df) - len(original_df):,}")
        r2.metric("Missing after cleaning", f"{int(cleaned_df.isna().sum().sum()):,}")
        r3.metric("Duplicates after cleaning", f"{int(cleaned_df.duplicated().sum()):,}")

        with st.expander("Cleaning summary", expanded=True):
            st.dataframe(
                st.session_state["cleaning_report"],
                use_container_width=True
            )

        with st.expander("Cleaned data preview", expanded=False):
            st.dataframe(cleaned_df.head(20), use_container_width=True)

        csv_data = cleaned_df.to_csv(index=False).encode("utf-8")

        b1, b2 = st.columns(2)

        with b1:
            st.download_button(
                "Download Cleaned CSV",
                data=csv_data,
                file_name="cleaned_dataset.csv",
                mime="text/csv",
                use_container_width=True
            )

        with b2:
            if st.button("Use Cleaned Data for Analysis", type="primary", use_container_width=True):
                st.session_state["use_cleaned_data"] = True
                st.rerun()


with tab3:
    head_l, head_r = st.columns([4, 1])
    with head_l:
        section(
            "Chat with Your Dataset",
            "Ask about totals, averages, maximum values, group comparisons, and missing values."
        )
    with head_r:
        clear_clicked = st.button("Clear Chat", use_container_width=True)

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if clear_clicked:
        st.session_state.chat_history = []
        st.rerun()

    if not st.session_state.chat_history:
        st.caption("Try: \"What is the average of a column?\" or \"Which group has the highest total?\"")

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    question = st.chat_input("Ask a question about your dataset")

    if question:
        st.session_state.chat_history.append({
            "role": "user",
            "content": question
        })

        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            try:
                with st.spinner("Analyzing your question..."):
                    plan = create_analysis_plan(
                        question,
                        df.columns.tolist(),
                        numeric_columns
                    )

                    result = run_analysis(
                        df,
                        plan["operation"],
                        plan.get("column"),
                        plan.get("group_by")
                    )

                    answer = explain_result(question, result)

                st.markdown(answer)

                if isinstance(result, list):
                    st.dataframe(
                        pd.DataFrame(result),
                        use_container_width=True
                    )

                if isinstance(result, dict):
                    with st.expander("Raw result"):
                        st.json(result)

                fig = create_chart(df, plan)

                if fig is not None:
                    st.plotly_chart(
                        fig,
                        use_container_width=True
                    )
                    st.session_state["latest_chart"] = fig

                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": answer
                })

            except Exception as e:
                error_message = f"Unable to analyze the question: {e}"
                st.error(error_message)

                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": error_message
                })

with tab4:
    section("Automated Exploratory Data Analysis", "Statistics, data quality and relationships at a glance.")

    eda_a, eda_b, eda_c, eda_d = st.tabs([
        "Numerical Summary",
        "Missing Values",
        "Potential Outliers",
        "Correlations"
    ])

    with eda_a:
        if numeric_columns:
            st.dataframe(
                df[numeric_columns].describe().T,
                use_container_width=True
            )
        else:
            st.info("No numerical columns are available.")

    missing_df = pd.DataFrame({
        "Column": df.columns.astype(str),
        "Missing Count": df.isna().sum().values,
        "Missing Percentage": (
            df.isna().mean().mul(100).round(2).values
        )
    })

    with eda_b:
        st.dataframe(
            missing_df,
            use_container_width=True,
            column_config={
                "Missing Percentage": st.column_config.ProgressColumn(
                    "Missing Percentage",
                    format="%.2f%%",
                    min_value=0,
                    max_value=100
                )
            }
        )

    with eda_c:
        st.dataframe(
            pd.DataFrame(
                list(profile["potential_outlier_counts_iqr"].items()),
                columns=["Column", "Potential Outliers"]
            ),
            use_container_width=True
        )

    with eda_d:
        if len(numeric_columns) >= 2:
            corr = df[numeric_columns].corr()
            st.plotly_chart(
                __import__("plotly.express", fromlist=["imshow"]).imshow(
                    corr,
                    text_auto=True,
                    aspect="auto",
                    title="Numerical Correlation Matrix"
                ),
                use_container_width=True
            )
        else:
            st.info("At least two numerical columns are needed.")

    st.write("")
    with st.container(border=True):
        section("AI Insights", "Generate a written summary of the most important findings.")

        if st.button("Generate AI EDA Insights", type="primary"):
            try:
                with st.spinner("Generating EDA insights..."):
                    insights = generate_eda_insights(profile)

                st.session_state["eda_insights"] = insights

            except Exception as e:
                st.error(f"EDA generation failed: {e}")

        if st.session_state.get("eda_insights"):
            st.markdown(st.session_state["eda_insights"])

with tab5:
    section(
        "Generate PDF Report",
        "Include dataset statistics, data-quality findings, AI insights, and the latest generated chart."
    )

    with st.container(border=True):
        k1, k2, k3 = st.columns(3)
        k1.metric("Dataset", "Cleaned" if _active else "Original")
        k2.metric("AI insights", "Ready" if st.session_state.get("eda_insights") else "Will generate")
        k3.metric("Chart included", "Yes" if st.session_state.get("latest_chart") is not None else "No")

        pdf_clicked = st.button("Generate PDF", type="primary")

    if pdf_clicked:
        try:
            with st.spinner("Creating your PDF report..."):
                insights = st.session_state.get("eda_insights")

                if not insights:
                    insights = generate_eda_insights(profile)
                    st.session_state["eda_insights"] = insights

                figures = []

                if st.session_state.get("latest_chart") is not None:
                    figures.append(
                        st.session_state["latest_chart"]
                    )

                pdf_bytes = create_pdf_report(
                    df,
                    profile,
                    insights,
                    figures
                )

                st.session_state["pdf_bytes"] = pdf_bytes
                st.toast("PDF report is ready.")

        except Exception as e:
            st.error(f"PDF generation failed: {e}")

    if st.session_state.get("pdf_bytes"):
        st.success("Your report is ready to download.")
        st.download_button(
            "Download PDF Report",
            data=st.session_state["pdf_bytes"],
            file_name="ai_data_analysis_report.pdf",
            mime="application/pdf",
            type="primary"
        )

st.sidebar.divider()
st.sidebar.download_button(
    "Download Dataset as CSV",
    data=df.to_csv(index=False).encode("utf-8"),
    file_name="analyzed_dataset.csv",
    mime="text/csv",
    use_container_width=True
)