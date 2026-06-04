import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# ==================================================
# PAGE CONFIG
# ==================================================

st.set_page_config(
    page_title="Startup Analytics Dashboard",
    page_icon="🚀",
    layout="wide"
)

# ==================================================
# CUSTOM CSS
# ==================================================

st.markdown("""
<style>

.main {
    background-color: #0e1117;
}

.metric-card {
    background: #1f2937;
    padding: 15px;
    border-radius: 12px;
}

div[data-testid="metric-container"]{
    border:1px solid #374151;
    padding:10px;
    border-radius:10px;
    background-color:#111827;
}

</style>
""", unsafe_allow_html=True)

# ==================================================
# DATA LOADING
# ==================================================

@st.cache_data
def load_data():

    base_path = Path(__file__).parent

    csv_path = base_path / "data" / "startup_data.csv"

    if not csv_path.exists():
        st.error(f"Dataset not found: {csv_path}")
        st.stop()

    df = pd.read_csv(csv_path)

    return df

df = load_data()

# ==================================================
# HEADER
# ==================================================

st.title("🚀 Startup Analytics Dashboard")
st.markdown(
    "Comprehensive exploratory analysis of startup ecosystem data"
)

# ==================================================
# SIDEBAR FILTERS
# ==================================================

st.sidebar.header("Filters")

industry_filter = st.sidebar.multiselect(
    "Industry",
    sorted(df["Industry"].unique()),
    default=sorted(df["Industry"].unique())
)

region_filter = st.sidebar.multiselect(
    "Region",
    sorted(df["Region"].unique()),
    default=sorted(df["Region"].unique())
)

exit_filter = st.sidebar.multiselect(
    "Exit Status",
    sorted(df["Exit Status"].unique()),
    default=sorted(df["Exit Status"].unique())
)

filtered_df = df[
    (df["Industry"].isin(industry_filter))
    & (df["Region"].isin(region_filter))
    & (df["Exit Status"].isin(exit_filter))
]

# ==================================================
# KPI SECTION
# ==================================================

st.subheader("📊 Executive Summary")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Startups",
        f"{filtered_df.shape[0]:,}"
    )

with col2:
    st.metric(
        "Total Funding",
        f"${filtered_df['Funding Amount (M USD)'].sum():,.0f} M"
    )

with col3:
    st.metric(
        "Total Revenue",
        f"${filtered_df['Revenue (M USD)'].sum():,.0f} M"
    )

with col4:
    profitability = (
        filtered_df["Profitable"].mean() * 100
    )

    st.metric(
        "Profitability",
        f"{profitability:.1f}%"
    )

st.divider()

# ==================================================
# INDUSTRY ANALYSIS
# ==================================================

st.subheader("🏭 Industry Analysis")

c1, c2 = st.columns(2)

industry_funding = (
    filtered_df
    .groupby("Industry")["Funding Amount (M USD)"]
    .sum()
    .reset_index()
    .sort_values(
        "Funding Amount (M USD)",
        ascending=False
    )
)

fig = px.bar(
    industry_funding,
    x="Industry",
    y="Funding Amount (M USD)",
    title="Funding by Industry"
)

c1.plotly_chart(
    fig,
    use_container_width=True
)

industry_revenue = (
    filtered_df
    .groupby("Industry")["Revenue (M USD)"]
    .mean()
    .reset_index()
)

fig = px.pie(
    industry_revenue,
    names="Industry",
    values="Revenue (M USD)",
    title="Average Revenue Distribution"
)

c2.plotly_chart(
    fig,
    use_container_width=True
)

# ==================================================
# REGION ANALYSIS
# ==================================================

st.subheader("🌍 Regional Analysis")

region_stats = (
    filtered_df
    .groupby("Region")
    .agg({
        "Valuation (M USD)": "mean",
        "Revenue (M USD)": "mean"
    })
    .reset_index()
)

fig = px.bar(
    region_stats,
    x="Region",
    y="Valuation (M USD)",
    color="Revenue (M USD)",
    title="Average Valuation by Region"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ==================================================
# FUNDING VS VALUATION
# ==================================================

st.subheader("💰 Funding vs Valuation")

fig = px.scatter(
    filtered_df,
    x="Funding Amount (M USD)",
    y="Valuation (M USD)",
    color="Industry",
    size="Employees",
    hover_name="Startup Name",
    title="Funding vs Valuation"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ==================================================
# PROFITABILITY
# ==================================================

st.subheader("📈 Profitability by Industry")

profit_df = (
    filtered_df
    .groupby("Industry")["Profitable"]
    .mean()
    .reset_index()
)

profit_df["Profitable"] = (
    profit_df["Profitable"] * 100
)

fig = px.bar(
    profit_df,
    x="Industry",
    y="Profitable",
    color="Profitable",
    title="Profitability Rate (%)"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ==================================================
# STARTUP AGE
# ==================================================

st.subheader("⏳ Startup Age Distribution")

current_year = 2026

filtered_df = filtered_df.copy()

filtered_df["Startup Age"] = (
    current_year -
    filtered_df["Year Founded"]
)

fig = px.histogram(
    filtered_df,
    x="Startup Age",
    nbins=20,
    title="Startup Age Distribution"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ==================================================
# EXIT STATUS
# ==================================================

st.subheader("🏁 Exit Status Analysis")

exit_counts = (
    filtered_df["Exit Status"]
    .value_counts()
    .reset_index()
)

exit_counts.columns = [
    "Exit Status",
    "Count"
]

fig = px.pie(
    exit_counts,
    names="Exit Status",
    values="Count",
    title="Exit Status Distribution"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ==================================================
# CORRELATION MATRIX
# ==================================================

st.subheader("🔥 Correlation Analysis")

numeric_cols = [
    "Funding Rounds",
    "Funding Amount (M USD)",
    "Valuation (M USD)",
    "Revenue (M USD)",
    "Employees",
    "Market Share (%)"
]

corr = filtered_df[numeric_cols].corr()

fig = px.imshow(
    corr,
    text_auto=True,
    aspect="auto",
    title="Correlation Matrix"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ==================================================
# TOP STARTUPS
# ==================================================

st.subheader("🏆 Top 20 Startups by Valuation")

top_startups = (
    filtered_df
    .sort_values(
        "Valuation (M USD)",
        ascending=False
    )
    .head(20)
)

st.dataframe(
    top_startups[
        [
            "Startup Name",
            "Industry",
            "Region",
            "Valuation (M USD)",
            "Revenue (M USD)",
            "Employees"
        ]
    ],
    use_container_width=True
)

# ==================================================
# FUNDING DISTRIBUTION
# ==================================================

st.subheader("💵 Funding Distribution")

fig = px.box(
    filtered_df,
    x="Industry",
    y="Funding Amount (M USD)",
    color="Industry"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ==================================================
# MARKET SHARE ANALYSIS
# ==================================================

st.subheader("📌 Market Share Analysis")

top_market = (
    filtered_df
    .sort_values(
        "Market Share (%)",
        ascending=False
    )
    .head(15)
)

fig = px.bar(
    top_market,
    x="Startup Name",
    y="Market Share (%)",
    color="Industry",
    title="Top Market Share Leaders"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ==================================================
# AUTOMATED INSIGHTS
# ==================================================

st.subheader("🧠 Key Insights")

highest_revenue_industry = (
    filtered_df
    .groupby("Industry")
    ["Revenue (M USD)"]
    .mean()
    .idxmax()
)

highest_valuation_region = (
    filtered_df
    .groupby("Region")
    ["Valuation (M USD)"]
    .mean()
    .idxmax()
)

highest_funding_industry = (
    filtered_df
    .groupby("Industry")
    ["Funding Amount (M USD)"]
    .sum()
    .idxmax()
)

st.success(
    f"""
    Highest Revenue Industry: {highest_revenue_industry}

    Highest Valuation Region: {highest_valuation_region}

    Most Funded Industry: {highest_funding_industry}

    Overall Profitability Rate: {profitability:.2f}%

    Total Funding Raised:
    ${filtered_df['Funding Amount (M USD)'].sum():,.0f} Million
    """
)

# ==================================================
# RAW DATA
# ==================================================

with st.expander("View Dataset"):
    st.dataframe(
        filtered_df,
        use_container_width=True
    )
