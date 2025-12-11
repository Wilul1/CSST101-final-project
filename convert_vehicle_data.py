"""
Convert the raw vehicle complaint text data into a properly formatted CSV
for ML model training.
"""
import pandas as pd
import re

# Your raw data - paste it here or load from file
raw_data_text = """Creation Date	Status	Completion Date	Service Request Number	Type of Service Request	License Plate	Vehicle Make/Model	Vehicle Color	Current Activity	Most Recent Action	How Many Days Has the Vehicle Been Reported as Parked?	Street Address	ZIP Code	X Coordinate	Y Coordinate	Ward	Police District	Community Area	SSA	Latitude	Longitude	Location	Historical Wards	2003-2015	Zip Codes	Community Areas	Census Tracts	Wards
2015-04-08T00:00:00.000	Completed	2015-04-09T00:00:00.000	15-01207496	Abandoned Vehicle Complaint	S48 3272	Bmw	Silver	FVI - Outcome	Vehicle was moved from original address requested	90	3020 N WATERLOO CT	60657	44	19	6	8	41.9370259	-87.64615133	{'latitude': '-87.64615132728282', 'longitude': '41.93702589972641'}
2016-10-13T00:00:00.000	Completed	2016-11-14T00:00:00.000	16-07176240	Abandoned Vehicle Complaint		FVI - Outcome	Vehicle was moved from original address requested		652 W ROSCOE ST	60657	1171215.844	1922811.93	44	19	6	8	41.94377029	-87.64661331	{'latitude': '-87.64661331410854', 'longitude': '41.943770285359875'}
2013-08-09T00:00:00.000	Completed	2013-08-23T00:00:00.000	13-01120231	Abandoned Vehicle Complaint	BUA0975	Cadillac	Green	FVI - Outcome	Vehicle was moved from original address requested	7	619 W CORNELIA AVE	60657	46	19	6	8	41.94557174	-87.64556542	{'latitude': '-87.64556541841895', 'longitude': '41.94557173829551'}
2011-09-02T00:00:00.000	Completed	2011-09-26T00:00:00.000	11-03714648	Abandoned Vehicle Complaint	626NKT	Mazda	Silver	FVI - Outcome	Need Vehicle Tow Report	7	437 W ROSCOE ST	60657	44	23	6	8	41.94324385	-87.64207184	{'latitude': '-87.64207184208428', 'longitude': '41.94324384654284'}
2016-10-24T00:00:00.000	Completed	2016-11-29T00:00:00.000	16-07402778	Abandoned Vehicle Complaint		FVI - Outcome	Vehicle was moved from original address requested		3016 N PINE GROVE AVE	60657	1172387.207	1920296.309	44	19	6	8	41.9370949	-87.64202372	{'latitude': '-87.64202372342636', 'longitude': '41.937094895726545'}
2017-06-15T00:00:00.000	Completed	2017-07-13T00:00:00.000	17-03952210	Abandoned Vehicle Complaint		FVI - Outcome	Vehicle was moved from original address requested		857 W FLETCHER ST	60657	1169946.534	1921098.85	44	19	6	8	41.93887732	-87.65140774	{'latitude': '-87.65140774486167', 'longitude': '41.93887731692307'}
2012-08-10T00:00:00.000	Completed	2012-09-12T00:00:00.000	12-01434578	Abandoned Vehicle Complaint	UX9051	Dodge	Gray	FVI - Outcome	Need Vehicle Tow Report	180	2844 N CAMBRIDGE AVE	60657	44	19	6	8	41.93414843	-87.64292978	{'latitude': '-87.642929780827', 'longitude': '41.934148427843276'}
2017-01-26T00:00:00.000	Completed	2017-02-28T00:00:00.000	17-00474294	Abandoned Vehicle Complaint	X318847	Acura	Gold	FVI - Outcome	Vehicle was moved from original address requested	60	701 W BROMPTON AVE	60657	1171002.67	1923878.93	46	19	6	8	41.94645951	-87.64687364	{'latitude': '-87.64687364239323', 'longitude': '41.94645950995542'}
2012-10-17T00:00:00.000	Completed	2012-11-26T00:00:00.000	12-01766115	Abandoned Vehicle Complaint	A437819	Ford	Black	Place 7 Day Sticker	Follow on Activity was created	42	2900 N BURLING ST	60657	1170795.388	1919503.581	44	19	6	8	41.93464009	-87.64788858	{'latitude': '-87.64788858228572', 'longitude': '41.9346400853701'}
2015-09-02T00:00:00.000	Completed - Dup	2015-09-03T00:00:00.000	15-04531079	Abandoned Vehicle Complaint	RJD520	Buick	Black	FVI - Outcome	Create Work Order	30	510 W ROSCOE ST	60657	1172232.998	1922704.346	44	19	6	8	41.94345761	-87.64256199	{'latitude': '-87.642561993092', 'longitude': '41.94345761352975'}
2018-02-10T00:00:00.000	Completed	2018-03-12T00:00:00.000	18-00627826	Abandoned Vehicle Complaint	594YFW	Toyota	Blue	Place 7 Day Sticker	Vehicle was moved from original address requested	30	2847 N HALSTED ST	60657	1170439.69	1919220.11	44	19	6	8	41.93411833	-87.64891528	{'latitude': '-87.64891527863726', 'longitude': '41.934118332992334'}
2012-05-18T00:00:00.000	Completed	2012-08-06T00:00:00.000	12-00942920	Abandoned Vehicle Complaint	6JHZ201	Mazda	Red	FVI - Outcome	Need Vehicle Tow Report	45	520 W ALDINE AVE	60657	44	19	6	8	41.94236063	-87.64291172	{'latitude': '-87.64291171896483', 'longitude': '41.9423606335504'}
2011-03-29T00:00:00.000	Completed	2011-04-06T00:00:00.000	11-00514837	Abandoned Vehicle Complaint	5543909	Lexus	Silver	FVI - Outcome	Return to Owner - Vehicle	7	2843 N BURLING ST	60657	44	19	6	8	41.93397146	-87.64756356	{'latitude': '-87.64756356103372', 'longitude': '41.933971463137205'}
2015-11-02T00:00:00.000	Completed	2015-11-09T00:00:00.000	15-05904714	Abandoned Vehicle Complaint	UH1 W6H	Saturn	White	FVI - Outcome	Vehicle was moved from original address requested	30	3718 N PINE GROVE AVE	60613	46	19	6	8	41.95024979	-87.64712105	{'latitude': '-87.64712105390387', 'longitude': '41.95024979259934'}
2016-06-09T00:00:00.000	Completed - Dup	2016-06-09T00:00:00.000	16-04005807	Abandoned Vehicle Complaint			FVI - Outcome	Vehicle was moved from original address requested		3752 N PINE GROVE AVE	60613	1170872.071	1925386.595	46	19	6	8	41.95111042	-87.64764482	{'latitude': '-87.6476448216525', 'longitude': '41.95111042012269'}
2019-02-06T00:00:00.000	Completed	2019-03-15T00:00:00.000	19-00014320	Abandoned Vehicle Complaint	NONE	Construction Equipment	Blue	Initial Inspection	Proceed with Tow Case		703 W WELLINGTON	60657	1170995.366	1920180.45	44	19	6	8	41.93634302	-87.64700507	{'latitude': '-87.64700507185893', 'longitude': '41.936343021925346'}
2019-08-20T00:00:00.000	Completed	2019-08-26T00:00:00.000	19-00107121	Abandoned Vehicle Complaint	ILLINOIS LICENSE BN 22512	Toyota	Beige	Initial Inspection	Vehicle was moved from original address requested		555 W CORNELIA AVE	60657	1171676.19	1923701.198	46	19	6	8	41.94599026	-87.6443372	{'latitude': '-87.6443371995947', 'longitude': '41.94599026354412'}
2018-01-31T00:00:00.000	Completed - Dup	2018-01-31T00:00:00.000	18-00543031	Abandoned Vehicle Complaint	892T429	Nissan	White	FVI - Outcome	Create Work Order	21	437 W ALDINE AVE	60657	1172478.575	1922312.625	44	19	6	8	41.94216148	-87.64139472	{'latitude': '-87.64139472326463', 'longitude': '41.942161477554265'}
2016-07-20T00:00:00.000	Completed	2016-08-10T00:00:00.000	16-05098619	Abandoned Vehicle Complaint	DM6008	Honda	Black	FVI - Outcome	Vehicle was moved from original address requested	10	614 W BARRY AVE	60657	1171612.55	1920712.43	44	19	6	8	41.93800371	-87.64497431	{'latitude': '-87.64497431463727', 'longitude': '41.93800370996964'}"""

def determine_priority(days_parked, most_recent_action, current_activity):
    """Determine priority based on data"""
    # Convert days_parked to int
    try:
        if pd.isna(days_parked) or days_parked == '' or str(days_parked).strip() == '':
            days = 0
        else:
            days_str = str(days_parked).strip()
            # Remove non-numeric characters
            days_clean = re.sub(r'[^\d.]', '', days_str)
            if days_clean:
                days = int(float(days_clean))
                # Sanity check - if days seems too high, it might be a parsing error
                if days > 1000:
                    days = 0
            else:
                days = 0
    except:
        days = 0
    
    action = str(most_recent_action).lower()
    activity = str(current_activity).lower()
    
    # High priority: tow needed, blocking, or 60+ days
    if any(kw in action or kw in activity for kw in ['tow', 'blocking', 'hazard', 'emergency']):
        return 'High'
    if days >= 60:
        return 'High'
    
    # Medium priority: 30-59 days or work order needed
    if days >= 30 or 'work order' in action.lower():
        return 'Medium'
    
    # Low priority: less than 30 days, already moved, or minor issues
    return 'Low'

def create_description(row):
    """Create description from row data"""
    parts = []
    
    # Vehicle info
    vehicle = []
    make_model = row.get('Vehicle Make/Model', '')
    color = row.get('Vehicle Color', '')
    
    if pd.notna(make_model) and str(make_model).strip() and str(make_model).lower() != 'nan':
        vehicle.append(str(make_model).strip())
    if pd.notna(color) and str(color).strip() and str(color).lower() != 'nan':
        vehicle.append(str(color).strip())
    
    if vehicle:
        parts.append(f"{' '.join(vehicle)} vehicle")
    
    license_plate = row.get('License Plate', '')
    if pd.notna(license_plate) and str(license_plate).strip() and str(license_plate).lower() != 'nan':
        parts.append(f"License plate: {str(license_plate).strip()}")
    
    # Days parked - be careful with parsing
    days_col = 'How Many Days Has the Vehicle Been Reported as Parked?'
    days = row.get(days_col, '')
    if pd.notna(days) and str(days).strip() and str(days).lower() not in ['nan', '']:
        try:
            # Extract number from string if needed
            days_str = str(days).strip()
            # Remove any non-numeric characters except decimal point
            days_clean = re.sub(r'[^\d.]', '', days_str)
            if days_clean:
                days_int = int(float(days_clean))
                if 0 < days_int < 1000:  # Sanity check
                    parts.append(f"Parked for {days_int} days")
        except:
            pass
    
    # Action/Status
    action = row.get('Most Recent Action', '')
    if pd.notna(action) and str(action).strip() and str(action).lower() != 'nan':
        parts.append(f"Action: {str(action).strip()}")
    
    return '. '.join(parts) if parts else "Abandoned vehicle complaint"

def process_data():
    """Process the raw text data into ML format"""
    # Parse the text data
    lines = raw_data_text.strip().split('\n')
    
    # Get headers
    headers = [h.strip() for h in lines[0].split('\t')]
    
    # Parse data rows
    rows = []
    for line in lines[1:]:
        if line.strip():
            values = [v.strip() for v in line.split('\t')]
            if len(values) >= 10:  # At least some data
                row_dict = dict(zip(headers, values))
                rows.append(row_dict)
    
    # Create DataFrame
    df = pd.DataFrame(rows)
    
    # Print available columns for debugging
    print(f"\nAvailable columns in raw data: {list(df.columns)[:15]}...")
    
    # Process into ML format
    processed = []
    for idx, row in df.iterrows():
        # Get days parked with proper parsing
        days_col = 'How Many Days Has the Vehicle Been Reported as Parked?'
        days_raw = row.get(days_col, 0)
        try:
            if pd.isna(days_raw) or str(days_raw).strip() == '':
                days = 0
            else:
                days_str = re.sub(r'[^\d.]', '', str(days_raw))
                days = int(float(days_str)) if days_str else 0
                if days > 1000:  # Likely parsing error
                    days = 0
        except:
            days = 0
        
        action = row.get('Most Recent Action', '')
        activity = row.get('Current Activity', '')
        
        # Build location
        location_parts = []
        if pd.notna(row.get('Street Address')) and str(row['Street Address']).strip():
            location_parts.append(str(row['Street Address']))
        if pd.notna(row.get('ZIP Code')) and str(row['ZIP Code']).strip():
            location_parts.append(f"ZIP {row['ZIP Code']}")
        location = ', '.join(location_parts) if location_parts else "Location not specified"
        
        # Helper function to safely get column value
        def get_col(col_name, default=''):
            val = row.get(col_name, default)
            return val if pd.notna(val) else default
        
        # Build the record with all columns - using exact column names from raw data
        record = {
            'category': 'Others',  # Map to existing category
            'description': create_description(row),
            'location': location,
            'priority': determine_priority(days, action, activity),
            # Additional columns - using exact column names from the raw data
            'creation_date': get_col('Creation Date'),
            'status': get_col('Status'),
            'completion_date': get_col('Completion Date'),
            'service_request_number': get_col('Service Request Number'),
            'type_of_service_request': get_col('Type of Service Request'),
            'license_plate': get_col('License Plate'),
            'vehicle_make_model': get_col('Vehicle Make/Model'),
            'vehicle_color': get_col('Vehicle Color'),
            'current_activity': get_col('Current Activity'),
            'most_recent_action': get_col('Most Recent Action'),
            'days_parked': days,
            'street_address': get_col('Street Address'),
            'zip_code': get_col('ZIP Code'),
            'x_coordinate': get_col('X Coordinate'),
            'y_coordinate': get_col('Y Coordinate'),
            'ward': get_col('Ward'),
            'police_district': get_col('Police District'),
            'community_area': get_col('Community Area'),
            'ssa': get_col('SSA'),
            'latitude': get_col('Latitude'),
            'longitude': get_col('Longitude'),
            'location_full': get_col('Location'),
            'historical_wards_2003_2015': get_col('Historical Wards 2003-2015'),
            'zip_codes': get_col('Zip Codes'),
            'community_areas': get_col('Community Areas'),
            'census_tracts': get_col('Census Tracts'),
            'wards': get_col('Wards')
        }
        
        processed.append(record)
    
    result_df = pd.DataFrame(processed)
    result_df.to_csv('vehicle_dataset.csv', index=False)
    
    print(f"Processed {len(result_df)} records")
    print(f"\nPriority distribution:")
    print(result_df['priority'].value_counts())
    print(f"\nSaved to: vehicle_dataset.csv")
    print("\nNext steps:")
    print("1. Review vehicle_dataset.csv")
    print("2. Set DATASET_PATH='vehicle_dataset.csv' in app.py or as environment variable")
    print("3. Run: python app.py")
    
    return result_df

if __name__ == '__main__':
    process_data()

