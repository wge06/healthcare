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
    (df['Year'].isin(selected_year)) &
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
st.subheader("📈 Crude Rate")
fig1 = px.bar(filtered_df, x="Age Group", y="Crude Rate", color="Sex", barmode="group",title='Crude Rate by Age Group & Gender')


age_group_crude = (
    filtered_df.groupby('Age Group').agg({'Deaths': 'sum', 'Population': 'sum'}).reset_index()
)
age_group_crude['Crude Rate'] = (age_group_crude['Deaths'] / age_group_crude['Population']) * 1e5

fig4 = px.line(
    age_group_crude,
    x='Age Group',
    y='Deaths',
    markers=True,
    title='Crude Rate by Age Group'
)

fig5 = px.line(
    age_group_crude,
    x='Age Group',
    y='Crude Rate',
    markers=True,
    title='Crude Rate by Age Group'
)

deaths_by_year = (
    filtered_df.groupby('Year').agg({'Deaths': 'sum', 'Population': 'sum'}).reset_index()
)

fig6 = px.line(
    deaths_by_year,
    x='Year',
    y='Deaths',
    markers=True,
    title='Deaths by Year'
)


fig2 = px.bar(filtered_df, x="Age Group", y="Deaths", color="Sex", barmode="group",title='Drowning Deaths Demographics')



time_df = df[
    (df['Sex'].isin(selected_sex)) &
    (df['Age Group'].isin(selected_age))
].groupby(['Year', 'Sex'])['Deaths'].sum().reset_index()
fig3 = px.line(time_df, x="Year", y="Deaths", color="Sex",title='Deaths Trends by Gender')

# Row 1: 3 columns
col4, col5, col6 = st.columns(3)
with col4:
    st.plotly_chart(fig1, use_container_width=True)
with col5:
    st.plotly_chart(fig5, use_container_width=True)
with col6:
    st.plotly_chart(fig4, use_container_width=True)
    
st.subheader("📊 Deaths")

# Row 2: 3 more columns
col7, col8, col9 = st.columns(3)
with col7:
    st.plotly_chart(fig2, use_container_width=True)
with col8:
    st.plotly_chart(fig3, use_container_width=True)
with col9:
    st.plotly_chart(fig6, use_container_width=True)

st.markdown("""
---
ℹ️ *Data Source: [CDC WISQARS](https://wisqars.cdc.gov/)*
""")
