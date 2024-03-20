import streamlit as st
import pandas as pd
import numpy as np

# Function to load the data
def load_data(uploaded_file):
    if uploaded_file is not None:
        return pd.read_csv(uploaded_file)
    else:
        return pd.DataFrame()

# Title of the app
st.title('Mercedes Benz Sales Manager Panel')

# Instructions
st.markdown("## Upload a CSV file to get started.")

# Upload the dataset and save as csv
uploaded_file = st.file_uploader("Upload your input CSV file", type=["csv"])

# Load the data only after the file is uploaded
if uploaded_file is not None:
    df = load_data(uploaded_file)
    
    # Sidebar for model selection
    if 'MODEL' in df.columns:
        selected_models = st.sidebar.multiselect('Select Models', options=df['MODEL'].unique())
        
        # Filter data based on selected models
        if selected_models:
            filtered_data = df[df['MODEL'].isin(selected_models)]
        else:
            filtered_data = pd.DataFrame()
    else:
        st.error('The uploaded file does not contain a "MODEL" column.')

    if not filtered_data.empty:
        # Display data for selected models

        # Summary stats
        st.write('Summary Stats')
        summary_stats = filtered_data[['PRIORDAY SALES', 'M-T-D SALES', 'Y-T-D SALES', 'DEALER INV', 'DAYS SUPPLY']].agg(['sum', 'mean', 'min', 'max'])
        st.table(summary_stats)

        # Sales trends (example: M-T-D SALES)
        st.write('Monthly-to-Date Sales Trends')
        mt_d_sales = filtered_data[['MODEL', 'M-T-D SALES']].set_index('MODEL')
        st.bar_chart(mt_d_sales)

        # Detailed data view
        st.write('Detailed View')
        st.dataframe(filtered_data)
        
    else:
        st.warning('No models selected or available in the dataset.')
else:
    st.info('Awaiting CSV file to be uploaded.')
