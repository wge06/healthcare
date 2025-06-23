import streamlit as st
import pandas as pd
import plotly.express as px

st.title("USA Drowning - Geographic Distribution")


# Load the cleaned data
df = pd.read_csv("state.csv")

# Clean numeric columns
numeric_columns = ['Deaths', 'Population', 'Crude Rate', 'Years of Potential Life Lost']
for col in numeric_columns:
    df[col] = df[col].replace('--', pd.NA)
    df[col] = df[col].str.replace(',', '', regex=False)
    df[col] = df[col].str.replace('*', '', regex=False)
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Convert Year to numeric
df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
df.dropna(subset=['Year', 'Deaths', 'Population', 'Crude Rate','State'], inplace=True)

st.set_page_config(page_title="USA Drowning Dashboard", layout="wide")
st.title("📊 USA Drowning Dashboard")
st.markdown("""
This dashboard presents USA drowning mortality-related statistics derived from CDC's WISQARS data.
Use the filters to explore trends by year, sex, and State.
""")

# Sidebar filters
years = sorted(df['Year'].dropna().unique().astype(int))
sexes = df['Sex'].dropna().unique()
age_groups = df['State'].dropna().unique()

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
selected_age = st.sidebar.multiselect("Select State", age_groups, default=list(age_groups))
# Filtered data
filtered_df = df[
    (df['Year'].isin(selected_years)) &
    (df['Sex'].isin(selected_sex)) &
    (df['State'].isin(selected_age))
]

# Crude rate metric variable as sum of deaths per 100,000 population which adjusted based on dashboard filters
crude_rate_metric = (filtered_df['Deaths'].sum() / filtered_df['Population'].sum())*100000
# KPIs
col1, col2, col3 = st.columns(3)
col1.metric("Total Deaths", f"{int(filtered_df['Deaths'].sum()):,}")
col2.metric("Avg Crude Rate", f"{crude_rate_metric:.2f}")
col3.metric("Total YPLL", f"{int(filtered_df['Years of Potential Life Lost'].sum()):,}")

# Map state names to abbreviations if needed
state_abbrev = {
    'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR',
    'California': 'CA', 'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE',
    'Florida': 'FL', 'Georgia': 'GA', 'Hawaii': 'HI', 'Idaho': 'ID',
    'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA', 'Kansas': 'KS',
    'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD',
    'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS',
    'Missouri': 'MO', 'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV',
    'New Hampshire': 'NH', 'New Jersey': 'NJ', 'New Mexico': 'NM', 'New York': 'NY',
    'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH', 'Oklahoma': 'OK',
    'Oregon': 'OR', 'Pennsylvania': 'PA', 'Rhode Island': 'RI', 'South Carolina': 'SC',
    'South Dakota': 'SD', 'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT',
    'Vermont': 'VT', 'Virginia': 'VA', 'Washington': 'WA', 'West Virginia': 'WV',
    'Wisconsin': 'WI', 'Wyoming': 'WY'
}
filtered_df['State Code'] = filtered_df['State'].map(state_abbrev)

# Create choropleth map
fig = px.choropleth(
    filtered_df,
    locations='State Code',
    locationmode='USA-states',
    color='Deaths',
    scope='usa',
    color_continuous_scale='Reds',
    labels={'Total Deaths': 'Deaths'},
    title='Total Deaths by U.S. State'
)

# Display in Streamlit
st.plotly_chart(fig, use_container_width=True)


# # Row 1: 3 columns
# col3, col4, col5 = st.columns(3)
# with col3:
#     st.plotly_chart(fig4, use_container_width=True)
# with col4:
#     st.plotly_chart(fig1, use_container_width=True)
# with col5:
#     st.plotly_chart(fig5, use_container_width=True)
    

st.markdown("""
ℹ️ *Data Source: [CDC WISQARS](https://wisqars.cdc.gov/)*
""")
