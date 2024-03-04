# APHRC DSE Inspire Hackathon 2024

## Overview

This project showcases the integration of health data from two sources, a Health and Demographic Surveillance System (HDSS), and health facility records, using record linkage techniques. The aim is to identify and merge records corresponding to the same individuals across datasets.

## Project Files

- **APHRC_DSE_Inspire_Hackathon_2024.ipynb:** Jupyter notebook containing the Python code and analysis for the record linkage process.
- **app.py:** Streamlit web application code for performing record linkage.
- **metadata_v3.pdf:** Metadata document providing information about the datasets and variables.
- **synthetic_facility_v3.csv:** CSV file containing synthetic data representing the health facility dataset.
- **synthetic_hdss_v3.csv:** CSV file containing synthetic data representing the HDSS dataset.

## Libraries Used

- pandas
- numpy
- recordlinkage

## Project Structure

### 1. Data Cleaning
Both datasets (`hdss_df` and `facility_df`) are loaded and cleaned to standardize text fields using the `recordlinkage.preprocessing.clean` function.

### 2. Feature Engineering
New columns, such as `fullname`, are created in both datasets by combining relevant name columns. Date columns are converted to datetime formats for consistency.

### 3. Duplicate Handling
Duplicates are checked based on combinations of `fullname`, `dob`, and `sex` columns. The 'nationalid' column in the health facility data is identified as unsuitable for unique identification.

### 4. Record Linkage
In the record linkage process, an indexer is initialized to create pairs of potentially matching records from 'hdss_df' and 'facility_df' based on the 'firstname' attribute. These pairs are then stored in the 'pairs' variable. Subsequently, a Compare object is introduced to define and apply various comparison measures. This includes utilizing string similarity measures for both 'firstname' and 'fullname', comparing date of birth ('dob'), and exact matching for the 'sex' attribute. The compute method is employed to calculate comparison scores, and an aggregate score is computed for each pair. Pairs with an aggregate score of 3 or more are identified as true matches, signifying a substantial similarity across the considered attributes. In the final stages, a k-means classifier is enlisted for model training and prediction. The classifier is trained on potential matches, excluding the score column, and leverages this training to predict matched indices.

### 5. Model Evaluation
First, true matches are identified by considering pairs with an aggregate score of 3 or more, resulting in 3545 matches. A k-means classifier is employed to predict matched indices based on the characteristics of potential matches, and the results are presented as a MultiIndex. A confusion matrix is then computed, offering insights into the true positives, false positives, false negatives, and true negatives, with counts of 3529, 16, 2, and 30546, respectively. The calculated F-score, a combined precision and recall metric, stands at an impressive 0.997, affirming the model's robust performance in accurately linking records while minimizing both false positives and false negatives.

### 6. Resulting Dataset
The resulting dataset (`hdss_facility`) contains matched records from both datasets. The dataset is deduplicated, resulting in a final dataset with unique records.

### 7. Record Linkage Function
A function named `perform_record_linkage` is defined to handle the record linkage process utilizing the created record linkage model in the `APHRC_DSE_Inspire_Hackathon_2024.ipynb` file.

### 8. Streamlit Web Application
The Streamlit app includes the following features:
- A title and a sidebar for users to upload the HDSS and facility CSV files.
- Upon uploading files, the datasets are read into Pandas DataFrames (`hdss_df` and `facility_df`).
- A button labeled 'Perform Record Linkage' triggers the record linkage process when clicked.
- The results of the record linkage, i.e., potential matched records, are displayed in the main section of the web app.

## User Interaction

Users can interact with the application through the following steps:
- Upload HDSS and facility CSV files using the sidebar file uploaders.
- Click the 'Perform Record Linkage' button to trigger the record linkage process.
- Explore the results, i.e., potential matched records, displayed in the main section of the web app.

## Future Improvements

- Enhance the user interface with additional features and visualizations.
- Optimize the record linkage algorithm for larger datasets.
- Include options for customizing matching thresholds.
- Deploy the app to enhance accessibility.

## Dependencies

The code relies on the following Python libraries:
- streamlit
- pandas
- recordlinkage

## Instructions

1. Clone the repository to your local machine.
2. Install the required dependencies using the following command:
   ```bash
   pip install streamlit pandas recordlinkage

## Streamlit App Execution

To run the Streamlit app, use the following command in your terminal:
```bash
streamlit run app.py
