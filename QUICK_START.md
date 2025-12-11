# Quick Start Guide - Using Your Vehicle Dataset

Your vehicle complaint data has been processed and is ready to use!

## ✅ What's Been Done

1. **Dataset Processed**: Your raw vehicle complaint data has been converted to `vehicle_dataset.csv`
2. **Priority Assigned**: Each record has been assigned a priority (High/Medium/Low) based on:
   - Days parked (60+ days = High, 30-59 = Medium, <30 = Low)
   - Action type (tow requests = High priority)
   - Current activity status

## 🚀 Next Steps

### Option 1: Use the Processed Dataset (Recommended)

The app is already configured to use `vehicle_dataset.csv` if it exists. Just run:

```bash
python app.py
```

The model will automatically train on your vehicle dataset when the app starts.

### Option 2: Use a Different Dataset

If you have more data or want to use a different file:

1. **Set environment variable:**
   ```bash
   # Windows
   set DATASET_PATH=your_dataset.csv
   
   # Linux/Mac
   export DATASET_PATH=your_dataset.csv
   ```

2. **Or edit app.py:**
   ```python
   DATASET_PATH = 'your_dataset.csv'
   ```

## 📊 Dataset Statistics

- **Total Records**: 19
- **Priority Distribution**:
  - High: 6 records
  - Medium: 5 records
  - Low: 8 records

## 🔄 Processing More Data

If you have more vehicle complaint data:

1. **Save as CSV/Excel** with these columns:
   - Type of Service Request
   - License Plate
   - Vehicle Make/Model
   - Vehicle Color
   - How Many Days Has the Vehicle Been Reported as Parked?
   - Street Address
   - ZIP Code
   - Most Recent Action
   - Current Activity

2. **Use the processing script:**
   ```python
   from process_vehicle_dataset import process_raw_data
   process_raw_data('your_new_data.csv', 'processed_dataset.csv')
   ```

3. **Update the dataset path** in `app.py` or via environment variable

## 🎯 Testing the Integration

1. Start the app: `python app.py`
2. Navigate to `http://localhost:5000/submit`
3. Submit a test request with category "Others" (since vehicle complaints are mapped to this category)
4. The ML model will predict priority based on your dataset

## 📝 Notes

- Vehicle complaints are currently mapped to the "Others" category
- If you want to add "Abandoned Vehicle Complaint" as a separate category, you'll need to:
  1. Update the category in `vehicle_dataset.csv` from "Others" to "Abandoned Vehicle Complaint"
  2. Add it to your form categories in the templates
  3. Add rules in `krr_engine.py` if needed

## 🐛 Troubleshooting

**Model not training on dataset:**
- Check that `vehicle_dataset.csv` exists in the project directory
- Verify the file has columns: category, description, location, priority
- Check the console output for any error messages

**Low accuracy:**
- Add more training data (aim for 100+ records)
- Ensure priority labels are correct
- Check data quality in descriptions



