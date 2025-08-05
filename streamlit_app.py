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
High school graduates around the globe make a hefty investment of their time and resources to pursue a bachelor's degree, but only 64% graduate within 6 years (NCES IPEDS, 2023). This 
figure has not improved much over the last 20+ years, when the same graduation rate was 58% in 2001. 

Which schools are succeeding when it comes to graduation rates, which ones are failing, and can exploring the data help us figure out why?
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

    with st.expander('What is IPEDS?'): # https://docs.streamlit.io/develop/api-reference/layout/st.expander
        '''
        The Integrated Postsecondary Education Data System (IPEDS), 
        curated by the National Center for Education Statistics (NCES), 
        contains a wide range of data from colleges, universities, 
        and other institutions of higher education that participate 
        in federal financial aid programs.

        Check out the [NCES website](https://nces.ed.gov/ipeds/) 
        for more information.
        '''

    with st.expander('Definitions'): # https://docs.streamlit.io/develop/api-reference/layout/st.expander
        '''
        **Graduation Rate**: The 6-year graduation rate among full-time, first-time students seeking a bachelor's or equivalent degree

        **Public**: An educational institution whose programs and activities are operated by publicly elected or appointed school officials and which is supported primarily by public funds.

        **Private**: A private (not-for-profit) institution in which the individual(s) or agency in control receives no compensation, other than wages, rent, or other expenses for the assumption of risk. These include both independent not-for-profit schools and those affiliated with a religious organization.

        **Financial Aid**: Includes grants, loans, assistantships, scholarships, waivers, discounts, benefits, and other monies provided to students to meet expenses.

        **Pell Grant**: A federal grant that provides grant assistance to eligible students with demonstrated financial need to help meet education expenses.

        **Federal Loans**: Monies borrowed via the federal government that must be repaid for which the student is the designated borrower.
        '''
    
    with st.expander('Who are we?'): 
        '''
        We are Group 2 from MESA8417, Summer 2025: 
        * Avi Bauer 
        * Zhengyu Fan
        * Margeau Jong
        '''

# ------ END SIDEBAR ------


# Filter data
ipeds_filtered = ipeds_df if sector == "All schools" else ipeds_df[ipeds_df["Control_of_institution"] == sector]

n_size = ipeds_filtered.shape[0]

ipeds_filtered['rate_ft'] = ipeds_filtered['Graduation_rate_Bachelor_6_years_total']/100
avg_outcome=ipeds_filtered['rate_ft'].mean()

# ------ MAP SECTION ------ 
# st.header(f"What do Graduation Rates {'' if sector=='All schools' else f'of {sector} Schools'} Look Like Across the USA?")
st.markdown(f"## Across :green[{n_size}] {'Schools' if sector=='All schools' else f'{sector} Schools'} in the USA, the Average Graduation Rate is :blue[{avg_outcome:.2%}]")

# Include a selector for colormap metric
state_metric = st.radio(
    label="Select the metric for colormap using radio buttons below. Select a state on the map to focus on that state in the lower graphs.",
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
    state_scheme = "greens"
elif state_metric == "State Overall Graduation Rate":
    state_metric_chosen = "Graduation_rate_Bachelor_6_years_total"
    state_metric_name = "Avg. Grad Rate (%)"
    state_scheme = "blues"

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
    color=alt.Color(f"{state_metric_chosen}:Q", title=state_metric_name).scale(scheme=state_scheme),
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

# Assign state ID to session_state
st.session_state.state_id = state_map["selection"]["state"][0]["id"] if len(state_map["selection"]["state"]) != 0 else None

# Filter data again
ipeds_refiltered = ipeds_filtered if len(state_map["selection"]["state"]) == 0 else ipeds_filtered[ipeds_filtered["id"] == st.session_state.state_id]

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
    st.header(f"Grad Rate Distribution for {'' if sector=='All schools' else sector} Schools in {'the USA' if len(state_map['selection']['state'])==0 else state_map['selection']['state'][0]['state']}")
    st.markdown(f"Including **:green[{n_size}]** Schools with a **:blue[{avg_outcome:.2%}]** Avg Graduation Rate")
    
    # Histogram of grad rates
    hist = alt.Chart(ipeds_refiltered).mark_bar(color='#58b568').encode(
        x=alt.X("Graduation_rate_Bachelor_6_years_total").bin().scale(domain=(0, 100)).title("Graduation Rate (%)"),
        y=alt.Y("count()", title="Frequency")
    )

    st.altair_chart(hist, use_container_width=True)
    
# 2nd column
with col2:
    st.header(f"Grad Rates vs. Financial Aid at {'' if sector=='All schools' else sector} Schools in {'the USA' if len(state_map['selection']['state'])==0 else state_map['selection']['state'][0]['state']}")
    st.markdown(f"Including **:green[{n_size}]** Schools with a **:blue[{avg_outcome:.2%}]** Avg Graduation Rate")
    
    # Dropdown filter
    bar_dimension = st.selectbox(label="Select aid type:",
                                 options=["Any Financial Aid",  
                                          "Pell Grants", 
                                          "Federal Loans"])
    
    # Select X-axis metric
    pell_footer = "" # lank unless Pell Grants is selected
    finaid_footer = ""
    fedloan_footer = ""
    if bar_dimension == "Any Financial Aid":
        x_metric = ["Percent_financial_aid", "Financial Aid (%)"]
        finaid_footer = "*Any financial aid includes grants, loans, assistantships, scholarships, waivers, discounts, benefits, and other monies provided to students to meet expenses."
    elif bar_dimension == "Pell Grants":
        x_metric = ["Percent_Pell_grants", "Pell Grants (%)"]
        pell_footer = "*A Pell Grant is a federal grant that provides grant assistance to eligible students with demonstrated financial need to help meet education expenses."
    elif bar_dimension == "Federal Loans":
        x_metric = ["Percent_federal_loans","Federal Loans (%)"]
        fedloan_footer = "*Federal loans are monies borrowed via the federal government that must be repaid for which the student is the designated borrower."
        
    # Add conditional notation about Pell Grants
    st.markdown(pell_footer)
    st.markdown(finaid_footer)
    st.markdown(fedloan_footer)
    
    # Create scatterplot
    scatter = alt.Chart(ipeds_refiltered).mark_circle(color='#2878b7').encode(
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

# ------ START TABLE ------

# Define data 
df_display_all = ipeds_refiltered[["institution_name",
                               "State",
                               "Control_of_institution",
                               "Graduation_rate_Bachelor_6_years_total",
                               "Percent_financial_aid",
                               "Percent_Pell_grants",
                               "Percent_federal_loans"]]
# hide in a dropdown
with st.expander("View the data"):

    # Allow for searching by name
    name_guess = st.text_input(label="Search for an institution by name:")

    # Filter data based on input
    df_display = df_display_all[df_display_all.institution_name.str.contains(name_guess, case=False)]

    # Add description
    st.markdown(f"Displaying **:green[{len(df_display)}]** {'' if sector=='All schools' else sector} Schools in {'the USA' if len(state_map['selection']['state'])==0 else state_map['selection']['state'][0]['state']}")
    
    # Display data table
    st.dataframe(data=df_display,
                 column_config={
                     "institution_name": "Institution Name",
                     "Control_of_institution":"Sector",
                     "Graduation_rate_Bachelor_6_years_total": "6-year Graduation Rate",
                     "Percent_financial_aid": "% Receiving Any Financial Aid",
                     "Percent_Pell_grants": "% Receiving Pell Grants",
                     "Percent_federal_loans": "% Receiving Fedeeral Loans"
                 },
                 hide_index=True,)

# ------ END TABLE ------
