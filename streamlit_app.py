import streamlit as st
import pandas as pd
import math
from pathlib import Path
import altair as alt

# Set top-level config here, such as page title & icon
st.set_page_config(
    layout="wide",
    page_title='IPEDS Exploration (MESA8417 Group 2)',
    page_icon=':school:', # This is an emoji shortcode. Could be a URL too.
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

'''
Map goes here.
'''

# ------ END MAP SECTION ------

# Add some spacing
''
''

# Filter data again


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
    ## Average Financial Aid (Grants and/or Loans)
    '''

    # Dropdown filter
    bar_dimension = st.selectbox(label="Aid type:",
                                 options=["Total Aid",  
                                          "Grant Aid", 
                                          "Student Loans"])
    
    # IF "Total Aid", make a pie chart
    if bar_dimension == "Total Aid":

        # Melt the data appropriately 
        third_pie_long = ipeds_filtered.melt(id_vars=["unitid"], 
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
        third_bars_long = ipeds_filtered.melt(id_vars=["unitid"], 
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
