import streamlit as st
import pandas as pd
import recordlinkage as rl
from recordlinkage.preprocessing import clean

# Function to perform record linkage
def perform_record_linkage(hdss_df, facility_df):
    # Preprocessing
    for col in facility_df.select_dtypes('object').columns:
        clean(facility_df[col], replace_by_none='[^ \\-\\_A-Za-z0-9]+', remove_brackets=True)
    facility_df['visitdate'] = pd.to_datetime(facility_df['visitdate'], format='%d-%m-%Y')    
    facility_df['fullname'] = facility_df['firstname'].fillna('') + ' ' + facility_df['lastname'].fillna('') + ' ' + facility_df['petname'].fillna('')
    facility_df['dob'] = pd.to_datetime(facility_df['dob'])
    

    for col in hdss_df.select_dtypes('object').columns:
        clean(hdss_df[col], replace_by_none='[^ \\-\\_A-Za-z0-9]+', remove_brackets=True)
    hdss_df['fullname'] = hdss_df['firstname'].fillna('') + ' ' + hdss_df['lastname'].fillna('') + ' ' + hdss_df['petname'].fillna('')
    hdss_df['dob'] = pd.to_datetime(hdss_df['dob'])

    # Record Linkage
    indexer = rl.Index()
    indexer.block(left_on='firstname', right_on='firstname')
    pairs = indexer.index(hdss_df, facility_df)

    compare = rl.Compare()
    compare.string('firstname', 'firstname', method='jarowinkler', label='firstname')
    compare.string('fullname', 'fullname', method='lcs', threshold=0.70, label='fullname')
    compare.date('dob', 'dob', label='dob')
    compare.exact('sex', 'sex', label='sex')

    potential_matches = compare.compute(pairs, hdss_df, facility_df)

    # Classification
    kmeans = rl.KMeansClassifier()
    kmeans.fit(potential_matches)
    matched_indices = kmeans.predict(potential_matches)

    # Merge datasets
    hdss_facility = pd.concat([hdss_df.loc[matched_indices.get_level_values(0)], facility_df.loc[matched_indices.get_level_values(1)]])
    hdss_facility.drop_duplicates(inplace=True)

    return hdss_facility

# Streamlit app
st.title('Record Linkage Application')

# Upload CSV files
st.sidebar.title('Upload CSV files')
hdss_file = st.sidebar.file_uploader('Upload HDSS CSV file')
facility_file = st.sidebar.file_uploader('Upload Facility CSV file')

if hdss_file and facility_file:
    hdss_df = pd.read_csv(hdss_file)
    facility_df = pd.read_csv(facility_file)

    # Perform record linkage when button is clicked
    if st.sidebar.button('Perform Record Linkage'):
        # Call the function to perform record linkage
        merged_data = perform_record_linkage(hdss_df, facility_df)

        # Display merged data
        st.write('Merged Dataset:')
        st.write(merged_data)

        # Save merged data to CSV
        merged_data.to_csv('matched_data.csv', index=False)
        st.success('Merged dataset saved as matched_data.csv')
