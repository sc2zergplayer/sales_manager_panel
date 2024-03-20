import streamlit as st
import pandas as pd

# Function to load data
def load_data(uploaded_file):
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        
        # Forward-fill the 'Class' column to associate models with their respective classes
        df['Class'] = df['Class'].ffill()

        return df
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
    
    # Remove unwanted rows ('Total' and NaN rows)
    df = df[df['MODEL'].notna() & (df['MODEL'].str.lower() != "total")]

    # Create a multiselect for selecting one or more classes
    classes = df['Class'].unique()
    selected_classes = st.multiselect('Select Class(es)', options=classes)

    # Filter the models based on the selected classes
    if selected_classes:
        class_filtered_data = df[df['Class'].isin(selected_classes)]
        class_models = class_filtered_data['MODEL'].unique()
    else:
        class_filtered_data = pd.DataFrame()
        class_models = []

    # Update multiselect options with models of the selected class(es)
    selected_models = st.multiselect('Select Models', options=class_models)

    # Filter data based on selected models
    if selected_models:
        filtered_data = class_filtered_data[class_filtered_data['MODEL'].isin(selected_models)]
    else:
        filtered_data = pd.DataFrame()

    if not filtered_data.empty:
        # Aggregate Sales Stats
        st.subheader('Aggregate Sales Stats')
        sales_stats = filtered_data[['PRIORDAY SALES', 'M-T-D SALES', 'Y-T-D SALES ']].agg(['sum', 'mean']).rename(index={'sum': 'Total', 'mean': 'Average'})
        st.table(sales_stats)

        # Aggregate Inventory Stats
        st.subheader('Aggregate Inventory Stats')
        inventory_stats = filtered_data[['DEALER INV', 'DAYS SUPPLY ', 'TOTAL AVAIL']].agg(['sum', 'mean']).rename(index={'sum': 'Total', 'mean': 'Average'})
        st.table(inventory_stats)

        # Detailed data view
        st.subheader('Detailed View')
        # Option to select columns to display
        cols_to_display = st.multiselect('Columns to display', options=filtered_data.columns.tolist(), default=filtered_data.columns.tolist())
        st.dataframe(filtered_data[cols_to_display])

    else:
        st.warning('Please select one or more models.')
else:
    st.info('Awaiting CSV file to be uploaded.')
