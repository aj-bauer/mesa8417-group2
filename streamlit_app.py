import streamlit as st
import pandas as pd
import math
from pathlib import Path

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

    # Perform any new column calculations, cleaning, etc. HERE

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
    ## Bar Graph (Aid, Pell, Loans)
    '''

# ------ END COLUMNS ------
