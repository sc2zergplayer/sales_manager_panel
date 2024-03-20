import streamlit as st
import pandas as pd

def load_data(uploaded_file):
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        df['Class'] = df['Class'].ffill()  # Fill down the 'Class' for all models
        return df
    return pd.DataFrame()

st.title('Mercedes Benz Sales Manager Panel')

uploaded_file = st.file_uploader("Upload your input CSV file", type=["csv"])

if uploaded_file is not None:
    df = load_data(uploaded_file)
    df = df[df['MODEL'].notna() & ~df['MODEL'].str.lower().isin(["class", "total"])]
    
    classes = df['Class'].unique()
    selected_classes = st.multiselect('Select Classes', options=classes)
    
    # Automatically select models from the chosen classes
    if selected_classes:
        class_models = df[df['Class'].isin(selected_classes)]['MODEL'].unique()
    else:
        class_models = []

    selected_models = st.multiselect('Select Models', options=df['MODEL'].unique(), default=class_models)

    if selected_models:
        filtered_data = df[df['MODEL'].isin(selected_models)]
        
        # Aggregate Sales Stats
        st.write('Aggregate Sales Stats')
        sales_stats = filtered_data[['PRIORDAY SALES', 'M-T-D SALES', 'Y-T-D SALES ']].agg(['sum'])
        st.table(sales_stats)

        # Aggregate Inventory Stats
        st.write('Aggregate Inventory Stats')
        inventory_stats = filtered_data[['DEALER INV', 'DAYS SUPPLY ', 'TOTAL AVAIL']].agg(['sum'])
        st.table(inventory_stats)

        # Detailed data view
        st.write('Detailed View')
        cols_to_display = st.multiselect('Columns to display', options=filtered_data.columns.tolist(), default=filtered_data.columns.tolist())
        st.dataframe(filtered_data[cols_to_display])
else:
    st.info('Awaiting CSV file to be uploaded.')
