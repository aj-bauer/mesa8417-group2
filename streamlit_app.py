import streamlit as st
import pandas as pd
import math
from pathlib import Path
import altair as alt

# Set top-level config here, such as page title & icon
st.set_page_config(
    layout="wide",
    page_title='IPEDS Exploration (MESA8417 Group 2)',
    page_icon=':mortar_board:', # This is an emoji shortcode. Could be a URL too.
)

# -----------------------------------------------------------------------------

# Declare some useful functions.

@st.cache_data
def get_ipeds_data():

    """Grab cleaned IPEDS data from a CSV file,
    and perform any necessary data manipulation.
    """

    # Instead of a CSV on disk, you could read from an HTTP endpoint here too.
    DATA_FILENAME = Path(__file__).parent/'data/IPEDS_DATA_CLEAN.csv'
    ipeds_df = pd.read_csv(DATA_FILENAME)

    # Perform any new column calculations, cleaning, etc. HERE

    return ipeds_df

ipeds_df = get_ipeds_data()

# -----------------------------------------------------------------------------

# Draw the actual page

# Set the title and text that appears at the top of the page.
'''
# :mortar_board: IPEDS Exploration: Graduation Rates & Financial Aid in Schools of Higher Education
In the year 2001, data from the National Center for Education Statistics (NCES) shows that the 6-year Bachelor’s graduation rate among degree-seeking undergraduates at 
public 4-year or private not-for-profit 4-year universities was about 58% (U.S. Department of Education, 2023). Just over half of the students who were investing their 
time and resources into continued education were not completing their bachelor’s degree within 150% of the expected time frame, unlikely to reap a return on their lost 
time and money. In 2023, this has increased to about 64%. While this is an improvement, more analysis needs to be done to better understand the schools that better foster 
student success.
'''

# Add some spacing
''
''

# ------ SIDEBAR ------
with st.sidebar: # https://docs.streamlit.io/develop/api-reference/layout/st.sidebar

    # Filters
    st.subheader("Filters")

    sector = st.radio(label="Sector:",
                      options=["All schools", "Public", "Private not-for-profit"],
                      index=0)

    # Background information
    st.subheader('Background')
    
    with st.expander('Who are we?'): # https://docs.streamlit.io/develop/api-reference/layout/st.expander
        '''
        We are Group 2 from MESA8417, Summer 2025: 
        * Avi Bauer 
        * Zhengyu Fan
        * Margeau Jong
        '''

    with st.expander('What is IPEDS?'):
        '''
        The Integrated Postsecondary Education Data System (IPEDS), 
        curated by the National Center for Education Statistics (NCES), 
        contains a wide range of data from colleges, universities, 
        and other institutions of higher education that participate 
        in federal financial aid programs.

        Check out the [NCES website](https://nces.ed.gov/ipeds/) 
        for more information.
        '''

# ------ END SIDEBAR ------


# Filter data
ipeds_filtered = ipeds_df if sector == "All schools" else ipeds_df[ipeds_df["Control_of_institution"] == sector]

n_size = ipeds_filtered.shape[0]

ipeds_filtered['rate_ft'] = ipeds_filtered['Graduation_rate_Bachelor_6_years_total']/100
avg_outcome=ipeds_filtered['rate_ft'].mean()

# ------ MAP SECTION ------ 
st.header(f"What do Graduation Rates {'' if sector=='All schools' else f'of {sector} Schools'} Look Like Across the USA?")

st.subheader(f"Number of {'Schools' if sector=='All schools' else f'{sector} Schools'}: {n_size}  \nAverage Graduation Rate: {avg_outcome:.2%} ")

# Use two columns to show n_size and avg_outcome
'''
col_a, col_b = st.columns(spec=2, gap="medium")

with col_a:
    st.subheader(n_size)
    st.markdown(f"Num of {'Schools' if sector=='All schools' else f'{sector} Schools'}")

with col_b:
    st.subheader(f"{avg_outcome:.2%}")
    st.markdown("Avg Graduation Rate")
'''

# Include a selector for colormap metric
state_metric = st.radio(
    label="Select metric for colormap:",
    options=["State Overall Graduation Rate",
             "Number of Schools per State"],
    horizontal=True,
    captions=["Average 6-year graduation rate (%)",
             f"{'Public and Private not-for-profit' if sector=='All schools' else sector} schools"]
)
# Assign values based on radio choice
if state_metric == "Number of Schools per State":
    state_metric_chosen = "unitid"
    state_metric_name = "Num. of Schools"
elif state_metric == "State Overall Graduation Rate":
    state_metric_chosen = "Graduation_rate_Bachelor_6_years_total"
    state_metric_name = "Avg. Grad Rate (%)"

# Aggregate the schools per state and overall grad rate
ipeds_state_metric = ipeds_filtered.groupby(["state", "id"]).agg({"unitid":"count", "Graduation_rate_Bachelor_6_years_total":"mean"}).reset_index()

# Define a pointer selection
click_state = alt.selection_point(name="state", fields=["id", "state"])
# Define a condition on the opacity encoding depending on the selection
opacity = alt.when(click_state).then(alt.value(1)).otherwise(alt.value(0.2))
# Define state data source
states = alt.topo_feature('https://cdn.jsdelivr.net/npm/vega-datasets@v1.29.0/data/us-10m.json', 'states')
# Generate map
chloropleth = alt.Chart(states).mark_geoshape(tooltip=True).transform_lookup(
    lookup='id',
    from_=alt.LookupData(ipeds_state_metric, 'id', ["unitid", "Graduation_rate_Bachelor_6_years_total", "state"])
).encode(
    color=alt.Color(f"{state_metric_chosen}:Q", title=state_metric_name),
    opacity=opacity,
    tooltip=[alt.Tooltip(field="state", title="State:"),
             alt.Tooltip(field="unitid", title="Num. of Schools:"),
             alt.Tooltip(field="Graduation_rate_Bachelor_6_years_total", format=".2f", formatType="number", title="Avg. Grad Rate (%):")]
).project(
    type='albersUsa'
).add_params(
    click_state
)
# Run map, return selected state value
state_map = st.altair_chart(chloropleth, on_select="rerun")

# Debugger
# st.markdown(f"{state_map}")

# Filter data again
ipeds_refiltered = ipeds_filtered if len(state_map["selection"]["state"]) == 0 else ipeds_filtered[ipeds_filtered["id"] == state_map["selection"]["state"][0]["id"]]

# ------ END MAP SECTION ------

# Add some spacing
''
'' 

# ------ COLUMNS ------

col1, col2 = st.columns(spec=2, gap="medium") # https://docs.streamlit.io/develop/api-reference/layout/st.columns

n_size = ipeds_refiltered.shape[0]

ipeds_refiltered['rate_ft'] = ipeds_refiltered['Graduation_rate_Bachelor_6_years_total']/100
avg_outcome=ipeds_refiltered['rate_ft'].mean()

# First column
with col1:
    st.header(f"Grad Rates of {'' if sector=='All schools' else sector} Schools in {'the USA' if len(state_map['selection']['state'])==0 else state_map['selection']['state'][0]['state']}")
    st.markdown(f"Including **{n_size}** Schools with a **{avg_outcome:.2%}** Avg Graduation Rate")
    
    # Histogram of grad rates
    hist = alt.Chart(ipeds_refiltered).mark_bar().encode(
        x=alt.X("Graduation_rate_Bachelor_6_years_total").bin().title("Graduation Rate (%)"),
        y=alt.Y("count()", title="Frequency")
    )

    st.altair_chart(hist, use_container_width=True)
    
# 2nd column
with col2:
    st.header(f"Grad Rates vs. Financial Aid at {'' if sector=='All schools' else sector} Schools in {'the USA' if len(state_map['selection']['state'])==0 else state_map['selection']['state'][0]['state']}")
    st.markdown(f"Including **{n_size}** Schools with a **{avg_outcome:.2%}** Avg Graduation Rate")
    
    # Dropdown filter
    bar_dimension = st.selectbox(label="Select aid type:",
                                 options=["Any Financial Aid",  
                                          "Pell Grants*", 
                                          "Federal Loans"])
    
    # Select X-axis metric
    pell_footer = "" # lank unless Pell Grants is selected
    if bar_dimension == "Any Financial Aid":
        x_metric = ["Percent_financial_aid", "Financial Aid (%)"]
    elif bar_dimension == "Pell Grants*":
        x_metric = ["Percent_Pell_grants", "Pell Grants (%)"]
        pell_footer = "*A Pell Grant is a federal grant awarded to college students meeting the criteria for financial neediness."
    elif bar_dimension == "Federal Loans":
        x_metric = ["Percent_federal_loans","Federal Loans (%)"]

    # Add conditional notation about Pell Grants
    st.markdown(pell_footer)
    
    # Create scatterplot
    scatter = alt.Chart(ipeds_refiltered).mark_circle().encode(
        x=alt.X(x_metric[0], title=f"Students Receiving {x_metric[1]}").scale(domain=(0, 100)),
        y=alt.Y("Graduation_rate_Bachelor_6_years_total", title="Graduation Rate (%)").scale(domain=(0, 100)),
        tooltip=[alt.Tooltip(field="institution_name", title="School:"),
                 alt.Tooltip(field="Graduation_rate_Bachelor_6_years_total", title="Grad Rate (%):"),
                 alt.Tooltip(field=x_metric[0], title=f"{x_metric[1]}:")]
    )

    # Add a regression line
    line = scatter.transform_regression(
        x_metric[0],
        "Graduation_rate_Bachelor_6_years_total"
    ).mark_line(clip=True).encode(
        color=alt.ColorValue("red")
    )
    
    scatter_line = scatter + line
    
    st.altair_chart(scatter_line, use_container_width=True)
    
        
# ------ END COLUMNS ------
