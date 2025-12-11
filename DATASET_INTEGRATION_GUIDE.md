# Dataset Integration Guide

This guide explains how to integrate your own dataset into the ML-Based Priority Ranking system.

## Quick Start

1. **Prepare your dataset** in CSV, Excel, or JSON format
2. **Set the dataset path** (see options below)
3. **Run the application** - the model will automatically train on your dataset

## Dataset Format

Your dataset must include these columns:

| Column | Required | Description | Example |
|--------|----------|-------------|---------|
| `category` | ✅ Yes | Type of service request | "Streetlight issue", "Waste collection" |
| `description` | ✅ Yes | Detailed description | "Broken streetlight on Main Street" |
| `location` | ⚠️ Optional | Address/location | "Main Street, Barangay 123" |
| `priority` | ✅ Yes | Priority level | "High", "Medium", or "Low" |

### Priority Values

The priority column must contain one of these values (case-insensitive):
- **High** (or: H, 1, Urgent)
- **Medium** (or: M, 2, Normal)
- **Low** (or: L, 3, Minor)

## Setting the Dataset Path

### Option 1: Environment Variable (Recommended)

**Windows:**
```cmd
set DATASET_PATH=C:\path\to\your\dataset.csv
python app.py
```

**Linux/Mac:**
```bash
export DATASET_PATH=/path/to/your/dataset.csv
python app.py
```

### Option 2: Edit app.py

Open `app.py` and modify this line:
```python
DATASET_PATH = 'your_dataset.csv'  # Change to your dataset path
```

### Option 3: Custom Column Names

If your dataset uses different column names, you can map them in `app.py`:

```python
COLUMN_MAPPING = {
    'Category': 'category',           # Your column name -> Expected name
    'Description': 'description',
    'Location': 'location',
    'Priority': 'priority'
}
```

## Supported File Formats

- **CSV** (`.csv`) - Most common, recommended
- **Excel** (`.xlsx`, `.xls`) - Supports multiple sheets (uses first sheet)
- **JSON** (`.json`) - Array of objects format

### CSV Example
```csv
category,description,location,priority
Streetlight issue,Broken light causing safety issue,Main Street,High
Waste collection,Garbage bin is full,Park Avenue,Medium
```

### JSON Example
```json
[
  {
    "category": "Streetlight issue",
    "description": "Broken light causing safety issue",
    "location": "Main Street",
    "priority": "High"
  }
]
```

## Retraining the Model

### Via Web Interface (Admin Panel)

1. Navigate to `/admin` in your browser
2. Use the retrain API endpoint (requires implementation in admin panel)

### Via API

```bash
curl -X POST http://localhost:5000/admin/retrain_model \
  -H "Content-Type: application/json" \
  -d '{"dataset_path": "path/to/your/dataset.csv"}'
```

### Via Python

```python
from ml_model import MLPriorityPredictor

# Initialize with your dataset
predictor = MLPriorityPredictor(dataset_path='your_dataset.csv')

# Retrain the model
accuracy = predictor.retrain_with_dataset()
print(f"Model accuracy: {accuracy:.2%}")
```

## Best Practices

1. **Data Quality**
   - Ensure descriptions are meaningful and detailed
   - Use consistent category names
   - Include a good mix of all priority levels

2. **Dataset Size**
   - Minimum: 20-30 records
   - Recommended: 100+ records for better accuracy
   - Try to balance priority distribution (not all High or all Low)

3. **Category Consistency**
   - Use the same category names as in your form
   - Common categories: "Waste collection", "Streetlight issue", "Road repair", etc.

4. **Description Quality**
   - Include relevant keywords (e.g., "urgent", "dangerous", "broken")
   - More detailed descriptions lead to better predictions

## Troubleshooting

### "Dataset file not found"
- Check that the file path is correct
- Use absolute path if relative path doesn't work
- Ensure the file exists and is readable

### "Missing required columns"
- Verify your dataset has `category`, `description`, and `priority` columns
- Check column names match exactly (case-sensitive after mapping)
- Use `COLUMN_MAPPING` if your columns have different names

### "No valid records found"
- Check that priority values are valid (High, Medium, Low)
- Ensure required columns don't have too many missing values
- Verify data types are correct

### Model accuracy is low
- Add more training data
- Ensure priority labels are correct
- Check for data quality issues
- Try balancing the dataset (equal distribution of priorities)

## Example Dataset

See `dataset_template.csv` in the project root for a sample dataset format.

## Need Help?

- Check the main README.md for general setup instructions
- Review the code comments in `ml_model.py` for technical details
- Ensure all dependencies are installed: `pip install -r requirements.txt`



