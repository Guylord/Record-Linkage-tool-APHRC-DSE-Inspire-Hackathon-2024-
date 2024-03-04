import streamlit as st
import pandas as pd
import recordlinkage as rl
from recordlinkage.preprocessing import clean

# Function to perform record linkage and return potential matches
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

    # Model
    kmeans = rl.KMeansClassifier()
    kmeans.fit(potential_matches)
    matched_indices = kmeans.predict(potential_matches)
    len(matched_indices)

    # Get matched records
    hdss_facility = pd.concat([hdss_df.loc[matched_indices.get_level_values(0)], facility_df.loc[matched_indices.get_level_values(1)]])
    hdss_facility.sort_values('firstname', inplace=True)
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

    # Set index for record linkage
    hdss_df.set_index('recnr', inplace=True)
    facility_df.set_index('recnr', inplace=True)

    # Perform record linkage when button is clicked
    if st.sidebar.button('Perform Record Linkage'):
        # Call the function to perform record linkage
        matched_records = perform_record_linkage(hdss_df, facility_df)

        # Display matched records
        st.write('Potential Matches:')
        st.write(matched_records)

        # Search Functionality
        search_name = st.text_input('Search Name')
        if search_name:
            filtered_records = matched_records[matched_records['firstname'].str.contains(search_name, case=False) | 
                                               matched_records['lastname'].str.contains(search_name, case=False)]
            st.write('Filtered Records:')
            st.write(filtered_records)

        # Editable Table
        st.write('Editable Merged Dataset:')
        with st.form(key='edit_form'):
            edited_data = matched_records.copy()
            editable_data = st.table(edited_data)
            submit_button = st.form_submit_button(label='Save Edited Data')

            if submit_button:
                edited_data.to_csv('edited_data.csv', index=False)
                st.success('Edited data saved as edited_data.csv')