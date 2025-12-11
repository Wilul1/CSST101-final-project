"""
Script to process raw vehicle complaint data into the ML model format
"""
import pandas as pd
import re
from datetime import datetime

def determine_priority(row):
    """
    Determine priority based on various factors:
    - Days parked (more days = higher priority)
    - Most Recent Action (some actions indicate urgency)
    - Status
    """
    days_parked = row.get('How Many Days Has the Vehicle Been Reported as Parked?', 0)
    if isinstance(days_parked, str):
        try:
            days_parked = int(re.findall(r'\d+', str(days_parked))[0]) if re.findall(r'\d+', str(days_parked)) else 0
        except:
            days_parked = 0
    elif pd.isna(days_parked):
        days_parked = 0
    else:
        days_parked = int(days_parked)
    
    most_recent_action = str(row.get('Most Recent Action', '')).lower()
    current_activity = str(row.get('Current Activity', '')).lower()
    
    # High priority indicators
    high_priority_keywords = ['tow', 'emergency', 'hazard', 'dangerous', 'blocking', 'urgent']
    if any(keyword in most_recent_action or keyword in current_activity for keyword in high_priority_keywords):
        return 'High'
    
    # Days parked logic
    if days_parked >= 60:  # 60+ days = high priority
        return 'High'
    elif days_parked >= 30:  # 30-59 days = medium priority
        return 'Medium'
    elif days_parked >= 7:  # 7-29 days = medium priority
        return 'Medium'
    else:  # Less than 7 days = low priority
        return 'Low'

def create_description(row):
    """Create a comprehensive description from available data"""
    parts = []
    
    # Vehicle info
    vehicle_info = []
    if pd.notna(row.get('Vehicle Make/Model')):
        vehicle_info.append(str(row['Vehicle Make/Model']))
    if pd.notna(row.get('Vehicle Color')):
        vehicle_info.append(str(row['Vehicle Color']))
    if pd.notna(row.get('License Plate')):
        vehicle_info.append(f"License: {row['License Plate']}")
    
    if vehicle_info:
        parts.append(f"Vehicle: {', '.join(vehicle_info)}")
    
    # Days parked
    days_parked = row.get('How Many Days Has the Vehicle Been Reported as Parked?', '')
    if pd.notna(days_parked) and str(days_parked).strip():
        parts.append(f"Reported parked for {days_parked} days")
    
    # Current activity
    if pd.notna(row.get('Current Activity')):
        parts.append(f"Status: {row['Current Activity']}")
    
    # Most recent action
    if pd.notna(row.get('Most Recent Action')):
        parts.append(f"Action: {row['Most Recent Action']}")
    
    # Service request number
    if pd.notna(row.get('Service Request Number')):
        parts.append(f"Request #{row['Service Request Number']}")
    
    return '. '.join(parts) if parts else "Abandoned vehicle complaint"

def process_raw_data(input_file, output_file='processed_vehicle_dataset.csv'):
    """
    Process raw vehicle complaint data into ML model format
    
    Args:
        input_file: Path to input CSV/Excel file with raw data
        output_file: Path to output CSV file
    """
    try:
        # Try to load as CSV first, then Excel
        try:
            df = pd.read_csv(input_file)
        except:
            df = pd.read_excel(input_file)
        
        print(f"Loaded {len(df)} records from {input_file}")
        print(f"Columns: {list(df.columns)}")
        
        # Process each row
        processed_data = []
        
        for idx, row in df.iterrows():
            # Category - map to "Others" or use "Abandoned Vehicle Complaint"
            category = "Others"  # You can change this to "Abandoned Vehicle Complaint" if you add it to your system
            
            # Description
            description = create_description(row)
            
            # Location
            location_parts = []
            if pd.notna(row.get('Street Address')):
                location_parts.append(str(row['Street Address']))
            if pd.notna(row.get('ZIP Code')):
                location_parts.append(f"ZIP {row['ZIP Code']}")
            if pd.notna(row.get('Ward')):
                location_parts.append(f"Ward {row['Ward']}")
            location = ', '.join(location_parts) if location_parts else "Location not specified"
            
            # Priority
            priority = determine_priority(row)
            
            processed_data.append({
                'category': category,
                'description': description,
                'location': location,
                'priority': priority
            })
        
        # Create DataFrame
        processed_df = pd.DataFrame(processed_data)
        
        # Save to CSV
        processed_df.to_csv(output_file, index=False)
        
        print(f"\nProcessed {len(processed_df)} records")
        print(f"\nPriority distribution:")
        print(processed_df['priority'].value_counts())
        print(f"\nSaved to: {output_file}")
        
        return processed_df
        
    except Exception as e:
        print(f"Error processing data: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def process_text_data(text_data, output_file='processed_vehicle_dataset.csv'):
    """
    Process raw text data (like what the user provided) into ML model format
    
    Args:
        text_data: Raw text string with tab/space separated data
        output_file: Path to output CSV file
    """
    # This is a simplified parser for the text format provided
    # For better results, save the data as CSV/Excel first
    
    lines = text_data.strip().split('\n')
    
    # Try to parse header
    if len(lines) > 0:
        headers = lines[0].split('\t') if '\t' in lines[0] else lines[0].split()
        print(f"Detected headers: {headers[:10]}...")  # Show first 10
    
    print("\nNote: For best results, please save your data as a CSV or Excel file first.")
    print("Then use: process_raw_data('your_file.csv', 'output.csv')")
    
    return None

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python process_vehicle_dataset.py <input_file.csv> [output_file.csv]")
        print("\nExample:")
        print("  python process_vehicle_dataset.py raw_data.csv processed_dataset.csv")
        print("\nOr use the function directly in Python:")
        print("  from process_vehicle_dataset import process_raw_data")
        print("  process_raw_data('raw_data.csv', 'processed_dataset.csv')")
    else:
        input_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else 'processed_vehicle_dataset.csv'
        process_raw_data(input_file, output_file)



