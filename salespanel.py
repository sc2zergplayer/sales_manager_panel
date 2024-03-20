import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
def load_data(uploaded_file):
    if uploaded_file is not None:
        # Check the file extension and load accordingly
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(uploaded_file)
        
        # Forward-fill 'Class' values to fill gaps
        df['Class'] = df['Class'].ffill()
        
        # Additionally, remove rows where 'Class' is still NaN after forward filling
        # This step handles cases where the first rows are NaN
        df = df.dropna(subset=['Class'])
        
        return df
    return pd.DataFrame()

st.title('Dealer Inventory/Sales Analysis Panel')

uploaded_file = st.file_uploader("Upload your input CSV or Excel file", type=["csv", "xlsx", "xls"])

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
        sales_stats = filtered_data[['PRIORDAY SALES', 'M-T-D SALES', 'Y-T-D SALES ', 'PRIOR MONTH SALES', 'ROLLING 30 DAY  SALES ']].agg(['sum'])
        st.dataframe(sales_stats)

        # Aggregate Inventory Stats
        st.write('Aggregate Inventory Stats')
        inventory_stats = filtered_data[['DEALER INV', 'DAYS SUPPLY ', 'TOTAL AVAIL', 'TOTAL D/S ', 'IN LOAD', 'VPC INV', 'ON THE WATER', 'PR NOT SHIPPED', 'SCHED NOT PR'  ]].agg(['sum'])
        st.dataframe(inventory_stats)

        # Detailed data view
        st.write('Detailed View')
        cols_to_display = st.multiselect('Columns to display', options=filtered_data.columns.tolist(), default=filtered_data.columns.tolist())
        st.dataframe(filtered_data[cols_to_display])
else:
    st.info('Awaiting CSV file to be uploaded.')
