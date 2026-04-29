import streamlit as st
import pandas as pd
from utils.data_loader import load_data
from datetime import datetime
from utils.aws_cost_explorer import fetch_aws_cost_data


def generate_finops_report(
    total_cost,
    avg_daily_cost,
    top_service,
    top_team,
    score,
    risk_level,
    projected_monthly_spend,
    monthly_budget,
    budget_gap,
    insights,
    recommendations
):
    report = f"""
FinSight - AWS FinOps Report
Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

EXECUTIVE SUMMARY
-----------------
Total Cloud Cost: ₹{total_cost:,.0f}
Average Daily Cost: ₹{avg_daily_cost:,.0f}
Top Cost Service: {top_service}
Top Spending Team: {top_team}

GOVERNANCE
----------
FinOps Governance Score: {score}/100
Risk Level: {risk_level}

BUDGET FORECAST
---------------
Projected Monthly Spend: ₹{projected_monthly_spend:,.0f}
Monthly Budget: ₹{monthly_budget:,.0f}
Budget Gap: ₹{budget_gap:,.0f}

AUTOMATED INSIGHTS
------------------
"""

    for insight in insights:
        report += f"- {insight}\n"

    report += """

OPTIMIZATION RECOMMENDATIONS
----------------------------
"""

    if recommendations:
        for rec in recommendations:
            report += f"- {rec}\n"
    else:
        report += "- No major optimization actions required.\n"

    return report


st.set_page_config(page_title="FinSight", layout="wide")

st.markdown("""
<style>
.main {
    background-color: #f8fafc;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

.metric-card {
    background-color: white;
    padding: 1.2rem;
    border-radius: 14px;
    border: 1px solid #e5e7eb;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

.section-title {
    font-size: 1.4rem;
    font-weight: 700;
    margin-bottom: 0.2rem;
}

.section-caption {
    color: #64748b;
    font-size: 0.95rem;
    margin-bottom: 1rem;
}

.hero-box {
    background: linear-gradient(135deg, #0f172a, #1e293b);
    padding: 2rem;
    border-radius: 18px;
    color: white;
    margin-bottom: 1.5rem;
}

.hero-title {
    font-size: 2.1rem;
    font-weight: 800;
}

.hero-subtitle {
    font-size: 1rem;
    color: #cbd5e1;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.title("FinSight")
st.sidebar.write("AWS FinOps Cost Intelligence")
st.sidebar.markdown("---")
st.sidebar.write("Built for cloud cost visibility, ownership, governance, and optimization.")

monthly_budget = st.sidebar.number_input(
    "Monthly Cloud Budget",
    min_value=0,
    value=500000,
    step=10000
)

# -----------------------------
# MAIN TITLE
# -----------------------------
st.title("FinSight - AWS Cloud Cost Accountability Platform")
st.markdown("""
<div class="hero-box">
    <div class="hero-title">FinSight</div>
    <div class="hero-subtitle">
        AWS Cloud Cost Intelligence Platform for FinOps governance, budget risk monitoring, anomaly detection, and optimization tracking.
    </div>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# DATA SOURCE SELECTION
# -----------------------------
data_source = st.radio(
    "Select Data Source",
    ["Upload CSV", "Demo AWS Cost Explorer", "Live AWS Cost Explorer"],
    horizontal=True
)

uploaded_file = None

if data_source == "Upload CSV":
    uploaded_file = st.file_uploader("Upload AWS Cost CSV", type=["csv"])

# -----------------------------
# LOAD DATA
# -----------------------------
if data_source == "Live AWS Cost Explorer":
    try:
        df = fetch_aws_cost_data(days=7)
        st.success("Live AWS Cost Explorer data loaded successfully.")
    except Exception as e:
        st.error("Live AWS integration failed. Using fallback sample dataset.")
        st.info("Reason: AWS credentials are missing, invalid, expired, or do not have Cost Explorer access.")
        df = load_data("data/aws_cost_sample.csv")

elif data_source == "Demo AWS Cost Explorer":
    df = load_data("data/aws_cost_sample.csv")
    st.success("Demo AWS Cost Explorer data loaded successfully.")
    st.info("This simulates AWS Cost Explorer output for demo purposes without requiring live AWS credentials.")

elif uploaded_file is not None:
    df = load_data(uploaded_file)
    st.success("Uploaded data loaded successfully.")

else:
    df = load_data("data/aws_cost_sample.csv")
    st.info("Using sample AWS cost data. Upload your own CSV to replace it.")

# -----------------------------
# VALIDATE DATA
# -----------------------------
required_columns = [
    "date", "service", "team", "project", "environment",
    "resource_id", "usage", "cost", "region", "owner"
]

missing_columns = [col for col in required_columns if col not in df.columns]

if missing_columns:
    st.error(f"Missing required columns: {missing_columns}")
    st.stop()

df["owner"] = df["owner"].fillna("").astype(str)

# -----------------------------
# SIDEBAR FILTERS
# -----------------------------
st.sidebar.subheader("Filters")

selected_teams = st.sidebar.multiselect(
    "Team",
    options=sorted(df["team"].unique()),
    default=sorted(df["team"].unique())
)

selected_services = st.sidebar.multiselect(
    "AWS Service",
    options=sorted(df["service"].unique()),
    default=sorted(df["service"].unique())
)

selected_environments = st.sidebar.multiselect(
    "Environment",
    options=sorted(df["environment"].unique()),
    default=sorted(df["environment"].unique())
)

st.sidebar.subheader("Date Filter")

min_date = df["date"].min()
max_date = df["date"].max()

date_range = st.sidebar.date_input(
    "Select Date Range",
    [min_date, max_date]
)

st.sidebar.subheader("Cost Filter")

min_cost = float(df["cost"].min())
max_cost = float(df["cost"].max())

cost_range = st.sidebar.slider(
    "Select Cost Range",
    min_value=min_cost,
    max_value=max_cost,
    value=(min_cost, max_cost)
)

selected_owners = st.sidebar.multiselect(
    "Owner",
    options=sorted(df["owner"].unique()),
    default=sorted(df["owner"].unique())
)

selected_projects = st.sidebar.multiselect(
    "Project",
    options=sorted(df["project"].unique()),
    default=sorted(df["project"].unique())
)

top_n = st.sidebar.slider(
    "Show Top N Records by Cost",
    min_value=5,
    max_value=50,
    value=20
)

filtered_df = df[
    (df["team"].isin(selected_teams)) &
    (df["service"].isin(selected_services)) &
    (df["environment"].isin(selected_environments)) &
    (df["owner"].isin(selected_owners)) &
    (df["project"].isin(selected_projects)) &
    (df["cost"].between(cost_range[0], cost_range[1])) &
    (df["date"].between(pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])))
]

filtered_df = filtered_df.sort_values(by="cost", ascending=False).head(top_n)

if filtered_df.empty:
    st.warning("No data matches selected filters.")
    st.stop()

# -----------------------------
# CORE KPI CALCULATIONS
# -----------------------------
total_cost = filtered_df["cost"].sum()
total_services = filtered_df["service"].nunique()
total_teams = filtered_df["team"].nunique()
total_projects = filtered_df["project"].nunique()

avg_daily_cost = filtered_df.groupby("date")["cost"].sum().mean()
top_service = filtered_df.groupby("service")["cost"].sum().idxmax()
top_team = filtered_df.groupby("team")["cost"].sum().idxmax()

prod_cost = filtered_df[filtered_df["environment"].str.lower() == "prod"]["cost"].sum()
dev_cost = filtered_df[filtered_df["environment"].str.lower() == "dev"]["cost"].sum()

dev_cost_percent = (dev_cost / total_cost) * 100 if total_cost > 0 else 0
prod_cost_percent = (prod_cost / total_cost) * 100 if total_cost > 0 else 0

untagged_df = filtered_df[
    (filtered_df["owner"].str.strip() == "") |
    (filtered_df["team"].isna()) |
    (filtered_df["project"].isna())
]

untagged_cost = untagged_df["cost"].sum()
untagged_cost_percent = (untagged_cost / total_cost) * 100 if total_cost > 0 else 0

service_costs = filtered_df.groupby("service")["cost"].sum()
top_service_cost_percent = (service_costs.max() / total_cost) * 100 if total_cost > 0 else 0

team_costs = filtered_df.groupby("team")["cost"].sum()
top_team_cost_percent = (team_costs.max() / total_cost) * 100 if total_cost > 0 else 0

days_recorded = filtered_df["date"].nunique()

if days_recorded > 0:
    current_spend = filtered_df["cost"].sum()
    daily_run_rate = current_spend / days_recorded
    projected_monthly_spend = daily_run_rate * 30
    budget_gap = projected_monthly_spend - monthly_budget
else:
    current_spend = 0
    projected_monthly_spend = 0
    budget_gap = 0

cost_per_team = total_cost / total_teams if total_teams > 0 else 0
cost_per_project = total_cost / total_projects if total_projects > 0 else 0

resource_count = filtered_df["resource_id"].nunique()
avg_cost_per_resource = total_cost / resource_count if resource_count > 0 else 0

highest_cost_resource = filtered_df.sort_values(by="cost", ascending=False).iloc[0]["resource_id"]
highest_cost_resource_value = filtered_df.sort_values(by="cost", ascending=False).iloc[0]["cost"]

cost_per_usage_unit = (
    total_cost / filtered_df["usage"].sum()
    if filtered_df["usage"].sum() > 0 else 0
)

daily_cost_df = filtered_df.groupby("date")["cost"].sum().reset_index()

if len(daily_cost_df) > 1:
    first_day_cost = daily_cost_df.iloc[0]["cost"]
    last_day_cost = daily_cost_df.iloc[-1]["cost"]
    cost_growth_percent = ((last_day_cost - first_day_cost) / first_day_cost) * 100 if first_day_cost > 0 else 0
    cost_volatility = daily_cost_df["cost"].std()
else:
    cost_growth_percent = 0
    cost_volatility = 0

# -----------------------------
# GOVERNANCE SCORE CALCULATION
# -----------------------------
score = 100
risk_reasons = []

if untagged_cost_percent > 0:
    score -= 20
    risk_reasons.append(f"{untagged_cost_percent:.1f}% of spend has missing ownership/tagging.")

if dev_cost_percent > 25:
    score -= 20
    risk_reasons.append(f"Dev environment contributes {dev_cost_percent:.1f}% of total spend.")

if top_service_cost_percent > 40:
    score -= 15
    risk_reasons.append(f"{top_service} contributes {top_service_cost_percent:.1f}% of total spend.")

if top_team_cost_percent > 50:
    score -= 15
    risk_reasons.append(f"{top_team} owns {top_team_cost_percent:.1f}% of total spend.")

if avg_daily_cost > 25000:
    score -= 10
    risk_reasons.append("Average daily cloud cost is above the expected threshold.")

score = max(score, 0)

if score >= 80:
    risk_level = "Low Risk"
elif score >= 60:
    risk_level = "Moderate Risk"
else:
    risk_level = "High Risk"

# -----------------------------
# OPTIMIZATION RECOMMENDATIONS CALCULATION
# -----------------------------
recommendations = []

ec2_cost = filtered_df[filtered_df["service"] == "EC2"]["cost"].sum()
ec2_percent = (ec2_cost / total_cost) * 100 if total_cost > 0 else 0

if ec2_percent > 40:
    savings = ec2_cost * 0.2
    recommendations.append(
        f"EC2 cost is high ({ec2_percent:.1f}%). Consider rightsizing instances or using reserved instances. Potential savings: ₹{savings:,.0f}"
    )

if dev_cost_percent > 25:
    savings = dev_cost * 0.3
    recommendations.append(
        f"Dev environment cost is {dev_cost_percent:.1f}%. Shut down idle resources after work hours. Potential savings: ₹{savings:,.0f}"
    )

if untagged_cost_percent > 0:
    recommendations.append(
        f"₹{untagged_cost:,.0f} spend is untagged. Enforce mandatory tagging for cost accountability."
    )

s3_cost = filtered_df[filtered_df["service"] == "S3"]["cost"].sum()
s3_percent = (s3_cost / total_cost) * 100 if total_cost > 0 else 0

if s3_percent > 30:
    savings = s3_cost * 0.25
    recommendations.append(
        f"S3 cost is {s3_percent:.1f}%. Move old data to cheaper storage tiers such as Glacier. Potential savings: ₹{savings:,.0f}"
    )

if top_team_cost_percent > 50:
    recommendations.append(
        f"{top_team} team owns majority of cost ({top_team_cost_percent:.1f}%). Review resource allocation and distribute workloads."
    )

# -----------------------------
# AUTOMATED INSIGHTS CALCULATION
# -----------------------------
insights = []

insights.append(
    f"{top_team} is the highest spending team with ₹{team_costs.max():,.0f} in cloud cost."
)

insights.append(
    f"{top_service} is the highest cost AWS service, contributing {top_service_cost_percent:.1f}% of total spend."
)

if dev_cost_percent > 25:
    insights.append(
        f"Dev environment spend is high at {dev_cost_percent:.1f}%. Review non-production workloads for shutdown or rightsizing."
    )

if untagged_cost_percent > 0:
    insights.append(
        f"Ownership gap detected: ₹{untagged_cost:,.0f} spend is missing complete ownership metadata."
    )

if score < 80:
    insights.append(
        "Cloud governance requires attention. Prioritize tagging, ownership review, and service-level cost concentration."
    )
else:
    insights.append(
        "Cloud spend is currently well-governed based on ownership, environment, and concentration checks."
    )

# -----------------------------
# ANOMALY DETECTION CALCULATION
# -----------------------------
anomaly_records = []

daily_cost = filtered_df.groupby("date")["cost"].sum().reset_index()
avg_daily_cost_anomaly = daily_cost["cost"].mean()

for _, row in daily_cost.iterrows():
    threshold = avg_daily_cost_anomaly * 1.5

    if row["cost"] > threshold:
        excess_cost = row["cost"] - avg_daily_cost_anomaly
        priority_score = min(100, round((excess_cost / total_cost) * 100, 2)) if total_cost > 0 else 0

        anomaly_records.append({
            "Anomaly Type": "Daily Spend Spike",
            "Date": row["date"].date(),
            "Service": "All Services",
            "Team": "Multiple",
            "Project": "Multiple",
            "Owner": "Multiple",
            "Actual Cost": row["cost"],
            "Expected Cost": avg_daily_cost_anomaly,
            "Excess Cost": excess_cost,
            "Priority Score": priority_score,
            "Severity": "High" if excess_cost > avg_daily_cost_anomaly else "Medium",
            "Reason": "Daily cloud spend is significantly above normal average."
        })

service_avg_cost = filtered_df.groupby("service")["cost"].mean()

for service in filtered_df["service"].unique():
    service_data = filtered_df[filtered_df["service"] == service]

    for _, row in service_data.iterrows():
        avg_cost = service_avg_cost[service]
        threshold = avg_cost * 1.5

        if row["cost"] > threshold:
            excess_cost = row["cost"] - avg_cost
            priority_score = min(100, round((excess_cost / total_cost) * 100, 2)) if total_cost > 0 else 0

            anomaly_records.append({
                "Anomaly Type": "Service Cost Spike",
                "Date": row["date"].date(),
                "Service": row["service"],
                "Team": row["team"],
                "Project": row["project"],
                "Owner": row["owner"],
                "Actual Cost": row["cost"],
                "Expected Cost": avg_cost,
                "Excess Cost": excess_cost,
                "Priority Score": priority_score,
                "Severity": "High" if excess_cost > avg_cost else "Medium",
                "Reason": f"{row['service']} cost is unusually high compared to its normal average."
            })

team_avg_cost = filtered_df.groupby("team")["cost"].mean()

for team in filtered_df["team"].unique():
    team_data = filtered_df[filtered_df["team"] == team]

    for _, row in team_data.iterrows():
        avg_cost = team_avg_cost[team]
        threshold = avg_cost * 1.5

        if row["cost"] > threshold:
            excess_cost = row["cost"] - avg_cost
            priority_score = min(100, round((excess_cost / total_cost) * 100, 2)) if total_cost > 0 else 0

            anomaly_records.append({
                "Anomaly Type": "Team Spend Spike",
                "Date": row["date"].date(),
                "Service": row["service"],
                "Team": row["team"],
                "Project": row["project"],
                "Owner": row["owner"],
                "Actual Cost": row["cost"],
                "Expected Cost": avg_cost,
                "Excess Cost": excess_cost,
                "Priority Score": priority_score,
                "Severity": "High" if excess_cost > avg_cost else "Medium",
                "Reason": f"{row['team']} team has abnormal cloud spend compared to its usual average."
            })

dev_df = filtered_df[filtered_df["environment"].str.lower() == "dev"]

if not dev_df.empty:
    dev_cost_total = dev_df["cost"].sum()
    dev_cost_percent_for_anomaly = (dev_cost_total / total_cost) * 100 if total_cost > 0 else 0

    if dev_cost_percent_for_anomaly > 25:
        expected_dev_cost = total_cost * 0.25
        excess_cost = dev_cost_total - expected_dev_cost
        priority_score = min(100, round((excess_cost / total_cost) * 100, 2)) if total_cost > 0 else 0

        anomaly_records.append({
            "Anomaly Type": "Dev Environment Overspend",
            "Date": "Multiple",
            "Service": "Multiple",
            "Team": "Multiple",
            "Project": "Multiple",
            "Owner": "Multiple",
            "Actual Cost": dev_cost_total,
            "Expected Cost": expected_dev_cost,
            "Excess Cost": excess_cost,
            "Priority Score": priority_score,
            "Severity": "High",
            "Reason": f"Dev environment consumes {dev_cost_percent_for_anomaly:.1f}% of total cloud spend."
        })

anomaly_df = pd.DataFrame(anomaly_records)

if not anomaly_df.empty:
    anomaly_df = anomaly_df.sort_values(by="Priority Score", ascending=False)

if risk_level == "High Risk":
    st.error("System Status: High Cost Risk")
elif risk_level == "Moderate Risk":
    st.warning("System Status: Moderate Cost Risk")
else:
    st.success("System Status: Cost Structure Healthy")

# -----------------------------
# COST TREND ANALYSIS
# -----------------------------
trend_df = filtered_df.groupby("date")["cost"].sum().reset_index()
trend_df = trend_df.sort_values(by="date")

# -----------------------------
# SERVICE GROWTH ANALYSIS
# -----------------------------
service_trend = filtered_df.groupby(["date", "service"])["cost"].sum().reset_index()

growth_data = []

for service in service_trend["service"].unique():
    temp = service_trend[service_trend["service"] == service].sort_values("date")

    if len(temp) > 1:
        first = temp.iloc[0]["cost"]
        last = temp.iloc[-1]["cost"]

        growth = ((last - first) / first) * 100 if first > 0 else 0

        growth_data.append({
            "Service": service,
            "Growth %": round(growth, 2)
        })

growth_df = pd.DataFrame(growth_data)

if not growth_df.empty:
    fastest_growing_service = growth_df.sort_values(by="Growth %", ascending=False).iloc[0]

# -----------------------------
# COST CONCENTRATION ANALYSIS
# -----------------------------
service_cost_df = filtered_df.groupby("service")["cost"].sum().reset_index()
service_cost_df = service_cost_df.sort_values(by="cost", ascending=False)

service_cost_df["cumulative_%"] = (
    service_cost_df["cost"].cumsum() / service_cost_df["cost"].sum()
) * 100

# -----------------------------
# ACTION TRACKER DATA
# -----------------------------
action_items = []

# EC2 action
if ec2_percent > 40:
    action_items.append({
        "Issue": "High EC2 Cost",
        "Owner": "Cloud Engineering",
        "Severity": "High",
        "Estimated Savings": ec2_cost * 0.2,
        "Recommended Action": "Review EC2 rightsizing and reserved instance options.",
        "Status": "Open"
    })

# Dev environment action
if dev_cost_percent > 25:
    action_items.append({
        "Issue": "Dev Environment Overspend",
        "Owner": "Engineering Teams",
        "Severity": "High",
        "Estimated Savings": dev_cost * 0.3,
        "Recommended Action": "Shut down idle dev resources after work hours.",
        "Status": "Open"
    })

# Untagged resources action
if untagged_cost_percent > 0:
    action_items.append({
        "Issue": "Missing Cost Ownership Tags",
        "Owner": "FinOps / Platform Team",
        "Severity": "Medium",
        "Estimated Savings": 0,
        "Recommended Action": "Enforce mandatory owner, team, project, and environment tags.",
        "Status": "Open"
    })

# S3 action
if s3_percent > 30:
    action_items.append({
        "Issue": "High S3 Storage Cost",
        "Owner": "Data Platform Team",
        "Severity": "Medium",
        "Estimated Savings": s3_cost * 0.25,
        "Recommended Action": "Move old or infrequently accessed data to cheaper storage tiers.",
        "Status": "Open"
    })

# Budget action
if budget_gap > 0:
    action_items.append({
        "Issue": "Projected Budget Breach",
        "Owner": "Finance / Cloud Governance",
        "Severity": "High",
        "Estimated Savings": budget_gap,
        "Recommended Action": "Review active workloads and approve immediate cost control measures.",
        "Status": "Open"
    })

action_tracker_df = pd.DataFrame(action_items)


if risk_level == "High Risk":
    st.error("🔴 System Status: High Cloud Cost Risk")
elif risk_level == "Moderate Risk":
    st.warning("🟠 System Status: Moderate Cloud Cost Risk")
else:
    st.success("🟢 System Status: Cloud Cost Structure Healthy")

# -----------------------------
# TABS
# -----------------------------
tabs = st.tabs([
    "📊 Dashboard",
    "🛡️ Governance",
    "💡 Optimization",
    "⚠️ Risk Monitoring",
    "📄 Reports"
])

# -----------------------------
# BURN RATE INTELLIGENCE
# -----------------------------
if daily_run_rate > 0:
    days_until_budget_exhausted = monthly_budget / daily_run_rate
else:
    days_until_budget_exhausted = 0

if projected_monthly_spend > monthly_budget:
    burn_status = "Over Budget Trajectory"
elif projected_monthly_spend > monthly_budget * 0.8:
    burn_status = "Near Budget Limit"
else:
    burn_status = "Healthy Burn Rate"


# -----------------------------
# TEAM BUDGET PRESSURE
# -----------------------------
team_budget_df = (
    filtered_df.groupby("team")["cost"]
    .sum()
    .reset_index()
    .sort_values(by="cost", ascending=False)
)

team_budget_df["Spend %"] = (team_budget_df["cost"] / total_cost) * 100

team_budget_df["Pressure Level"] = team_budget_df["Spend %"].apply(
    lambda x: "High" if x > 50 else "Medium" if x > 25 else "Low"
)


# -----------------------------
# TAB 1: DASHBOARD
# -----------------------------
with tabs[0]:

    with st.container(border=True):
        st.subheader("📊 Executive Summary")
        st.caption("High-level cloud cost performance indicators for leadership review.")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Cloud Cost", f"₹{total_cost:,.0f}")
        col2.metric("AWS Services", total_services)
        col3.metric("Teams", total_teams)
        col4.metric("Projects", total_projects)

        col5, col6, col7, col8 = st.columns(4)
        col5.metric("Avg Daily Cost", f"₹{avg_daily_cost:,.0f}")
        col6.metric("Top Cost Service", top_service)
        col7.metric("Top Spending Team", top_team)
        col8.metric("Dev Cost %", f"{dev_cost_percent:.1f}%")

        col9, col10, col11, col12 = st.columns(4)
        col9.metric("Cost per Team", f"₹{cost_per_team:,.0f}")
        col10.metric("Cost per Project", f"₹{cost_per_project:,.0f}")
        col11.metric("Avg Cost per Resource", f"₹{avg_cost_per_resource:,.0f}")
        col12.metric("Cost per Usage Unit", f"₹{cost_per_usage_unit:,.2f}")

        col13, col14, col15 = st.columns(3)
        col13.metric("Prod Cost %", f"{prod_cost_percent:.1f}%")
        col14.metric("Resource Count", resource_count)
        col15.metric("Highest Cost Resource", f"{highest_cost_resource} - ₹{highest_cost_resource_value:,.0f}")

        col16, col17 = st.columns(2)
        col16.metric("Cost Growth %", f"{cost_growth_percent:.1f}%")
        col17.metric("Cost Volatility", f"₹{cost_volatility:,.0f}")

        if cost_growth_percent > 20:
            st.warning("Rapid cost growth detected. Investigate scaling inefficiencies.")

        if cost_volatility > avg_daily_cost:
            st.warning("High cost volatility detected. Cloud usage is unstable.")

    st.markdown("---")

    with st.container(border=True):
        st.subheader("💰 Budget Breach Predictor")
        st.caption("Forecasts whether current cloud usage will exceed the monthly budget.")

        b1, b2, b3 = st.columns(3)
        b1.metric("Current Spend", f"₹{current_spend:,.0f}")
        b2.metric("Projected Monthly Spend", f"₹{projected_monthly_spend:,.0f}")
        b3.metric("Monthly Budget", f"₹{monthly_budget:,.0f}")

        if budget_gap > 0:
            st.error(f"Budget breach likely. Expected overspend: ₹{budget_gap:,.0f}")
        else:
            st.success(f"Budget is under control. Expected savings: ₹{abs(budget_gap):,.0f}")

    st.markdown("---")

    with st.container(border=True):
        st.subheader("Cost Trend Analysis")
        st.caption("Tracks how cloud spending evolves over time.")
        st.line_chart(trend_df.set_index("date"))

    st.markdown("---")

    with st.container(border=True):
        st.subheader("Service Growth Intelligence")
        st.caption("Identifies fastest growing cost drivers.")

        if not growth_df.empty:
            st.dataframe(growth_df.sort_values(by="Growth %", ascending=False), use_container_width=True)

            st.warning(
                f"Fastest growing service: {fastest_growing_service['Service']} "
                f"({fastest_growing_service['Growth %']}% growth)"
            )
        else:
            st.info("Not enough data available to calculate service growth.")

    st.markdown("---")

    with st.container(border=True):
        st.subheader("Cost Concentration Analysis")
        st.caption("Highlights top services driving majority of cloud cost.")

        st.bar_chart(service_cost_df.set_index("service")["cost"])

        top_services = service_cost_df[service_cost_df["cumulative_%"] <= 80]

        if len(top_services) == 0 and not service_cost_df.empty:
            top_services_count = 1
        else:
            top_services_count = len(top_services)

        st.info(
            f"Top {top_services_count} service(s) contribute to approximately 80% of total cloud cost."
        )

        st.markdown("---")

        with st.container(border=True):
            st.subheader("🔥 Burn Rate Intelligence")
            st.caption("Tracks how quickly the cloud budget is being consumed.")

            br1, br2, br3 = st.columns(3)

            br1.metric("Daily Burn Rate", f"₹{daily_run_rate:,.0f}")
            br2.metric("Days Until Budget Exhaustion", f"{days_until_budget_exhausted:.1f} days")
            br3.metric("Burn Status", burn_status)

            if burn_status == "Over Budget Trajectory":
                st.error("Current usage pattern will exceed the monthly cloud budget.")
            elif burn_status == "Near Budget Limit":
                st.warning("Cloud spend is approaching the monthly budget limit.")
            else:
               st.success("Cloud spend is within a healthy burn rate.")

        st.markdown("---")

        with st.container(border=True):
           st.subheader("Team Budget Pressure")
           st.caption("Shows which teams are consuming the highest share of cloud spend.")

           st.dataframe(team_budget_df, use_container_width=True)

           highest_pressure_team = team_budget_df.iloc[0]

           if highest_pressure_team["Pressure Level"] == "High":
               st.warning(
            f"{highest_pressure_team['team']} has high budget pressure, consuming "
            f"{highest_pressure_team['Spend %']:.1f}% of total cloud spend."
        )
# -----------------------------
# TAB 2: GOVERNANCE
# -----------------------------
with tabs[1]:

    with st.container(border=True):
        st.subheader("🛡️ FinOps Governance Score")
        st.caption("Evaluates tagging quality, ownership gaps, and cost governance risk.")

        g1, g2, g3 = st.columns(3)
        g1.metric("Governance Score", f"{score}/100")
        g2.metric("Risk Level", risk_level)
        g3.metric("Untagged Spend", f"₹{untagged_cost:,.0f}")

        if risk_reasons:
            st.warning("Key FinOps Risk Factors")
            for reason in risk_reasons:
                st.write(f"- {reason}")
        else:
            st.success("No major FinOps governance risks detected.")

    st.markdown("---")

    with st.container(border=True):
        st.subheader("Team Cost Accountability")

        showback = (
            filtered_df.groupby(["team", "project", "environment", "owner"])["cost"]
            .sum()
            .reset_index()
            .sort_values(by="cost", ascending=False)
        )

        st.dataframe(showback, use_container_width=True)

    st.markdown("---")

    with st.container(border=True):
        st.subheader("Detailed Cost Records")
        st.dataframe(filtered_df, use_container_width=True)

# -----------------------------
# TAB 3: OPTIMIZATION
# -----------------------------
with tabs[2]:

    with st.container(border=True):
        st.subheader("Optimization Recommendations")

        if recommendations:
            st.warning("Recommended Cost Optimization Actions")
            for r in recommendations:
                st.write(f"- {r}")
        else:
            st.success("Cloud usage is optimized.")

    st.markdown("---")

    with st.container(border=True):
        st.subheader("Automated FinOps Insights")

        for insight in insights:
            st.write(f"- {insight}")

        st.markdown("---")

    with st.container(border=True):
        st.subheader("✅ Action Tracker")
        st.caption("Tracks owners, actions, status, and estimated savings.")

        if not action_tracker_df.empty:
            display_action_df = action_tracker_df.copy()
            display_action_df["Estimated Savings"] = display_action_df["Estimated Savings"].apply(
                lambda x: f"₹{x:,.0f}" if isinstance(x, (int, float)) else x
            )

            st.dataframe(display_action_df, use_container_width=True)

            total_estimated_savings = action_tracker_df["Estimated Savings"].sum()
            open_actions = len(action_tracker_df[action_tracker_df["Status"] == "Open"])

            c1, c2 = st.columns(2)
            c1.metric("Open Actions", open_actions)
            c2.metric("Total Estimated Savings", f"₹{total_estimated_savings:,.0f}")
        else:
            st.success("No action items required.")

# -----------------------------
# TAB 4: ANOMALIES
# -----------------------------
with tabs[3]:

    with st.container(border=True):
        st.subheader("⚠️ Advanced Anomaly Detection")
        st.caption("Ranks abnormal cloud spend using severity and priority score.")

        if not anomaly_df.empty:
            total_anomalies = len(anomaly_df)
            high_severity_count = len(anomaly_df[anomaly_df["Severity"] == "High"])
            total_excess_cost = anomaly_df["Excess Cost"].sum()

            a1, a2, a3 = st.columns(3)
            a1.metric("Total Anomalies", total_anomalies)
            a2.metric("High Severity Issues", high_severity_count)
            a3.metric("Estimated Excess Cost", f"₹{total_excess_cost:,.0f}")

            st.error("Anomalies Detected")

            display_anomaly_df = anomaly_df.copy()

            display_anomaly_df["Actual Cost"] = display_anomaly_df["Actual Cost"].apply(lambda x: f"₹{x:,.0f}" if isinstance(x, (int, float)) else x)
            display_anomaly_df["Expected Cost"] = display_anomaly_df["Expected Cost"].apply(lambda x: f"₹{x:,.0f}" if isinstance(x, (int, float)) else x)
            display_anomaly_df["Excess Cost"] = display_anomaly_df["Excess Cost"].apply(lambda x: f"₹{x:,.0f}" if isinstance(x, (int, float)) else x)

            st.dataframe(display_anomaly_df, use_container_width=True)

            st.subheader("Anomaly Summary")
            for _, row in anomaly_df.iterrows():
                st.write(
                    f"- **Priority {row['Priority Score']}/100 | {row['Severity']} Risk**: "
                    f"{row['Anomaly Type']} | Team: {row['Team']} | ₹{row['Excess Cost']:,.0f}"
                )
        else:
            st.success("No anomalies detected.")

# -----------------------------
# TAB 5: REPORTS
# -----------------------------
with tabs[4]:

    with st.container(border=True):
        st.subheader("Download FinOps Report")

        report_text = generate_finops_report(
            total_cost=total_cost,
            avg_daily_cost=avg_daily_cost,
            top_service=top_service,
            top_team=top_team,
            score=score,
            risk_level=risk_level,
            projected_monthly_spend=projected_monthly_spend,
            monthly_budget=monthly_budget,
            budget_gap=budget_gap,
            insights=insights,
            recommendations=recommendations
        )

        st.download_button(
            label="Download FinOps Report",
            data=report_text,
            file_name="finsight_finops_report.txt",
            mime="text/plain"
        )