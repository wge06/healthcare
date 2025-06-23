import streamlit as st
import pandas as pd
import plotly.express as px

# Load the cleaned data
df = pd.read_csv("ethnicity.csv")

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
Use the filters to explore trends by year, sex, and Ethnicity.
""")

# Sidebar filters
years = sorted(df['Year'].dropna().unique().astype(int))
sexes = df['Sex'].dropna().unique()
age_groups = df['Ethnicity'].dropna().unique()

st.sidebar.header("🔎 Filters")
# selected_years = st.sidebar.multiselect(
#     "Select Year(s)",
#     options=years,
#     default=years  # This selects all years by default
# )

select_all_years = st.sidebar.checkbox("Select All Years", value=True)
if select_all_years:
    selected_years = st.sidebar.multiselect("Select Year(s)", years, default=years)
else:
    selected_years = st.sidebar.multiselect("Select Year(s)", years)
selected_sex = st.sidebar.multiselect("Select Sex", sexes, default=list(sexes))
selected_age = st.sidebar.multiselect("Select Ethnicity", age_groups, default=list(age_groups))
# Filtered data
filtered_df = df[
    (df['Year'].isin(selected_years)) &
    (df['Sex'].isin(selected_sex)) &
    (df['Ethnicity'].isin(selected_age))
]

# Crude rate metric variable as sum of deaths per 100,000 population which adjusted based on dashboard filters
crude_rate_metric = (filtered_df['Deaths'].sum() / filtered_df['Population'].sum())*100000
# KPIs
col1, col2, col3 = st.columns(3)
col1.metric("Total Deaths", f"{int(filtered_df['Deaths'].sum()):,}")
col2.metric("Avg Crude Rate", f"{crude_rate_metric:.2f}")
col3.metric("Total YPLL", f"{int(filtered_df['Years of Potential Life Lost'].sum()):,}")

# Charts
st.subheader("Ethnicity")
fig1 = px.bar(filtered_df, x="Ethnicity", y="Crude Rate", color="Sex", barmode="group",title='Crude Rate by Ethnicity & Gender')


age_group_crude = (
    filtered_df.groupby('Ethnicity').agg({'Deaths': 'sum', 'Population': 'sum'}).reset_index()
)
age_group_crude['Crude Rate'] = (age_group_crude['Deaths'] / age_group_crude['Population']) * 1e5

fig4 = px.line(
    age_group_crude,
    x='Ethnicity',
    y='Deaths',
    markers=True,
    title='Crude Rate by Ethnicity'
)

fig5 = px.line(
    age_group_crude,
    x='Ethnicity',
    y='Crude Rate',
    markers=True,
    title='Crude Rate by Ethnicity'
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


fig2 = px.bar(filtered_df, x="Ethnicity", y="Deaths", color="Sex", barmode="group",title='Drowning Deaths Demographics')



time_df = df[
    (df['Sex'].isin(selected_sex)) &
    (df['Ethnicity'].isin(selected_age))
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
    

st.markdown("""
ℹ️ *Data Source: [CDC WISQARS](https://wisqars.cdc.gov/)*
""")
