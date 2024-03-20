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

    # Create a dropdown for selecting a class
    classes = df['Class'].unique()
    selected_class = st.selectbox('Select Class', options=classes)

    # Filter the models based on the selected class
    class_models = df[df['Class'] == selected_class]['MODEL'].unique()
    
    # Update multiselect options with models of the selected class
    selected_models = st.multiselect('Select Models', options=class_models, default=class_models)

    # Filter data based on selected models
    if selected_models:
        filtered_data = df[df['MODEL'].isin(selected_models)]
        
        # Detailed data view
        st.write('Detailed View')
        # Option to select columns to display
        cols_to_display = st.multiselect('Columns to display', options=filtered_data.columns, default=filtered_data.columns)
        st.dataframe(filtered_data[cols_to_display])

    else:
        filtered_data = pd.DataFrame()
        st.warning('Please select one or more models.')
else:
    st.info('Awaiting CSV file to be uploaded.')
