import streamlit as st
import pandas as pd
import plotly.express as px

# Load the cleaned data
df = pd.read_csv("reports-data-export.csv")

# Clean numeric columns
numeric_columns = ['Deaths', 'Population', 'Crude Rate', 'Years of Potential Life Lost']
for col in numeric_columns:
    df[col] = df[col].replace('--', pd.NA)
    df[col] = df[col].str.replace(',', '', regex=False)
    df[col] = df[col].str.replace('*', '', regex=False)
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Convert Year to numeric
df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
df.dropna(subset=['Year', 'Deaths', 'Population', 'Crude Rate'], inplace=True)

st.set_page_config(page_title="USA Drowning Dashboard", layout="wide")
st.title("📊 USA Drowning Dashboard")
st.markdown("""
This dashboard presents USA drowning mortality-related statistics derived from CDC's WISQARS data.
Use the filters to explore trends by year, sex, and age group.
""")

# Sidebar filters
years = sorted(df['Year'].dropna().unique().astype(int))
sexes = df['Sex'].dropna().unique()
age_groups = df['Age Group'].dropna().unique()

st.sidebar.header("🔎 Filters")
selected_year = st.sidebar.selectbox("Select Year", years, index=len(years)-1)
selected_sex = st.sidebar.multiselect("Select Sex", sexes, default=list(sexes))
selected_age = st.sidebar.multiselect("Select Age Group", age_groups, default=list(age_groups))

# Filtered data
filtered_df = df[
    (df['Year'] == selected_year) &
    (df['Sex'].isin(selected_sex)) &
    (df['Age Group'].isin(selected_age))
]
# Crude rate metric variable as sum of deaths per 100,000 population which adjusted based on dashboard filters
crude_rate_metric = (filtered_df['Deaths'].sum() / filtered_df['Population'].sum())*100000
# KPIs
col1, col2, col3 = st.columns(3)
col1.metric("Total Deaths", f"{int(filtered_df['Deaths'].sum()):,}")
col2.metric("Avg Crude Rate", f"{crude_rate_metric:.2f}")
col3.metric("Total YPLL", f"{int(filtered_df['Years of Potential Life Lost'].sum()):,}")

# Charts
st.subheader("📈 Crude Rate by Age Group")
fig1 = px.bar(filtered_df, x="Age Group", y="Crude Rate", color="Sex", barmode="group")
st.plotly_chart(fig1, use_container_width=True)

age_group_crude = (
    filtered_df.groupby('Age Group').agg({'Deaths': 'sum', 'Population': 'sum'}).reset_index()
)
age_group_crude['Crude Rate'] = (age_group_crude['Deaths'] / age_group_crude['Population']) * 1e5

fig5 = px.line(
    age_group_crude,
    x='Age Group',
    y='Crude Rate',
    markers=True,
    title='Crude Rate by Age Group (Line Chart)'
)
st.plotly_chart(fig5, use_container_width=True)


import plotly.graph_objects as go

#Create the figure
fig_combo = go.Figure()

# Bar trace: Total deaths
fig_combo.add_trace(go.Bar(
    x=age_group_crude['Age Group'],
    y=age_group_crude['Deaths'],
    name='Total Deaths',
    marker_color='rgba(55, 83, 109, 0.7)',
    yaxis='y1'
))

# Line trace: Crude rate
fig_combo.add_trace(go.Scatter(
    x=age_group_crude['Age Group'],
    y=age_group_crude['Crude Rate'],
    name='Crude Rate per 100,000',
    mode='lines+markers',
    line=dict(color='firebrick', width=3),
    yaxis='y2'
))

# Step 3: Customize layout
fig_combo.update_layout(
    title=dict(text="Crude Rate and Total Deaths by Age Group"),
    xaxis=dict(title="Age Group"),
    yaxis=dict(
        title="Total Deaths",
        titlefont=dict(color="rgba(55, 83, 109, 1)"),
        tickfont=dict(color="rgba(55, 83, 109, 1)")
    ),
    yaxis2=dict(
    title="Crude Rate (per 100,000)",
    titlefont=dict(color="firebrick"),
    tickfont=dict(color="firebrick"),
    overlaying='y',
    side='right'
    ),
    legend=dict(x=0.01, y=0.99),
    barmode='group'
)

# Step 4: Show the chart in Streamlit
st.plotly_chart(fig_combo, use_container_width=True)

st.subheader("📊 Deaths by Age Group")
fig2 = px.bar(filtered_df, x="Age Group", y="Deaths", color="Sex", barmode="group")
st.plotly_chart(fig2, use_container_width=True)

st.subheader("📉 Trend of Deaths Over Time")
time_df = df[
    (df['Sex'].isin(selected_sex)) &
    (df['Age Group'].isin(selected_age))
].groupby(['Year', 'Sex'])['Deaths'].sum().reset_index()
fig3 = px.line(time_df, x="Year", y="Deaths", color="Sex")
st.plotly_chart(fig3, use_container_width=True)

st.markdown("""
---
ℹ️ *Data Source: [CDC WISQARS](https://wisqars.cdc.gov/)*
""")
