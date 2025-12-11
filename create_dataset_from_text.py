"""
Script to create a dataset CSV from the raw text data provided by the user
"""
import pandas as pd
import re

# Raw data provided by user (first few rows as example)
# You should save your full dataset as CSV/Excel first, then use process_vehicle_dataset.py

def parse_text_to_dataframe(text_data):
    """
    Parse the raw text data into a structured DataFrame
    This is a helper function - ideally you should have the data in CSV/Excel format
    """
    lines = text_data.strip().split('\n')
    
    # Extract headers (first line)
    headers_line = lines[0]
    headers = [h.strip() for h in headers_line.split('\t') if h.strip()]
    
    data_rows = []
    for line in lines[1:]:
        if line.strip():
            values = [v.strip() for v in line.split('\t')]
            if len(values) >= len(headers):
                row_dict = dict(zip(headers, values[:len(headers)]))
                data_rows.append(row_dict)
    
    return pd.DataFrame(data_rows)

# Example usage with the provided data
if __name__ == '__main__':
    print("=" * 60)
    print("Vehicle Dataset Processor")
    print("=" * 60)
    print("\nTo process your dataset:")
    print("1. Save your raw data as a CSV or Excel file")
    print("2. Run: python process_vehicle_dataset.py your_file.csv")
    print("\nOr use Python directly:")
    print("  from process_vehicle_dataset import process_raw_data")
    print("  process_raw_data('your_file.csv', 'processed_dataset.csv')")
    print("\n" + "=" * 60)



