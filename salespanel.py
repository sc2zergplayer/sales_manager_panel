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

if uploaded_file is not None:
    df = load_data(uploaded_file)

    # Clean the DataFrame to remove unwanted rows
    df = df.dropna(subset=['MODEL', 'Class'])  # Drop rows where 'MODEL' or 'Class' is NaN
    df = df[~df['MODEL'].str.lower().isin(["class", "total"])]  # Exclude rows with 'MODEL' as "class" or "Total"
    df['Class'] = df['Class'].str.strip()  # Strip whitespace from the 'Class' column if any

    # Create a dropdown for selecting a class
    classes = df['Class'].unique()
    selected_class = st.selectbox('Select Class', options=classes)

    # Filter the models based on the selected class
    class_models = df[df['Class'] == selected_class]['MODEL'].unique()
    selected_models = st.multiselect('Select Models', options=class_models)

    # Filter data based on selected models
    if selected_models:
        filtered_data = df[df['MODEL'].isin(selected_models)]
    else:
        filtered_data = pd.DataFrame()

    if not filtered_data.empty:
        # Display data for selected models

        # Adjusted column names with trailing spaces
        summary_stats = filtered_data[['PRIORDAY SALES', 'M-T-D SALES', 'Y-T-D SALES ', 'DEALER INV', 'DAYS SUPPLY ']].agg(['sum', 'mean', 'min', 'max'])
        st.dataframe(summary_stats)

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
