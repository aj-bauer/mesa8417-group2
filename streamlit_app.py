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

    # Recalc percent columns as percents
    p_cols = ["Percent_financial_aid",
              "Percent_Pell_grants",
              "Percent_grant_aid",
              "Percent_student_loans",
              "Percent_federal_loans"]
    for col in p_cols:
        ipeds_df[f"{col}_p"] = ipeds_df[col] / 100

    # Calculate percent of students NOT getting finaid
    ipeds_df["Percent_no_aid"] = 1 - ipeds_df["Percent_financial_aid_p"]

    # Perform any other new column calculations, cleaning, etc. HERE

    return ipeds_df

ipeds_df = get_ipeds_data()

# -----------------------------------------------------------------------------

# Draw the actual page

# Set the title and text that appears at the top of the page.
'''
# :school: IPEDS Exploration
(Subtitle goes here.)
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
        * Zhenyu Fan
        * Margeau Jong
        '''
    
    with st.expander('Who are you?'):
        '''
        [[UPDATE]] Here we can explain our proposed use case.
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


# ------ MAP SECTION ------ 
st.header(f"Where are {'Public and Private not-for-profit' if sector=='All schools' else sector} Schools of Higher Ed in the USA?")

# Include a selector for colormap metric
state_metric = st.radio(
    label="Select metric for colormap:",
    options=["Number of Schools per State",
             "State Overall Graduation Rate"],
    horizontal=True,
    captions=[f"{'Public and Private not-for-profit' if sector=='All schools' else sector} schools",
              "Average 6-year graduation rate (%)"]
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
click_state = alt.selection_point(name="state", fields=["id"])
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
st.markdown(f"{state_map}")

# Filter data again
ipeds_refiltered = ipeds_filtered if len(state_map["selection"]["state"]) == 0 else ipeds_filtered[ipeds_filtered["id"] == state_map["selection"]["state"][0]["id"]]

# ------ END MAP SECTION ------

# Add some spacing
''
'' 

# ------ COLUMNS ------

col1, col2, col3 = st.columns(spec=3, gap="small") # https://docs.streamlit.io/develop/api-reference/layout/st.columns

# First column
with col1:
    '''
    ## Sector Pie Chart?
    '''

with col2:
    '''
    ## Grad Rate Histogram
    '''

with col3:
    '''
    ## How many students receive financial aid?
    '''

    # Dropdown filter
    bar_dimension = st.selectbox(label="Aid type:",
                                 options=["Any Aid",  
                                          "Grant Aid", 
                                          "Student Loans"])
    
    # IF "Total Aid", make a pie chart
    if bar_dimension == "Any Aid":

        # Melt the data appropriately 
        third_pie_long = ipeds_refiltered.melt(id_vars=["unitid"], 
                                  value_vars=["Percent_financial_aid_p", "Percent_no_aid"],
                                  var_name="Got_aid", 
                                  value_name="Percent")

        # Make a pie chart of receiving aid vs. not
        third_chart = alt.Chart(third_pie_long).mark_arc(innerRadius=10).encode(
            theta="mean(Percent)",
            color="Got_aid"
        )

    # Otherwise, make a bar chart
    else:
        if bar_dimension == "Grant Aid":
            bar_dim = ["Percent_grant_aid_p", "Percent_Pell_grants_p"]
        elif bar_dimension == "Student Loans":
            bar_dim = ["Percent_student_loans_p", "Percent_federal_loans_p"]

    
        # Select and melt data
        third_bars_long = ipeds_refiltered.melt(id_vars=["unitid"], 
                                  value_vars=bar_dim,
                                  var_name="Cost_Type", 
                                  value_name="Avg_amount")

        # Make a bar chart!
        third_chart = alt.Chart(third_bars_long).mark_bar().encode(
            x=alt.X("Cost_Type"),
            y=alt.Y("mean(Avg_amount)", title="Fraction receiving Aid").scale(domain=(0, 1)),
            tooltip=alt.Tooltip(aggregate="mean",
                                field="Avg_amount",
                                format=".0%",
                                formatType="number",
                                title="Receiving Aid:",
                                )
        )
    
    st.altair_chart(third_chart)
        
# ------ END COLUMNS ------
