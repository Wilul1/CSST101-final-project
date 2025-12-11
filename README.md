# ML-Based Priority Ranking System for Service Requests

A comprehensive web application for managing service requests with ML-based priority prediction and rule-based advisory system.

## Features

- **Dashboard**: View statistics, pending/completed counts, and category graphs
- **Submit Request**: Submit service requests with automatic ML priority prediction
- **View All Requests**: Browse all requests with filtering and sorting
- **Request Details**: View full request information with ML priority and KRR advisories
- **Admin Panel**: Advanced filtering, sorting, and reporting capabilities

## Installation

### Quick Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the setup script to initialize the ML model and download required data:
```bash
python setup.py
```

3. Run the application:
```bash
python app.py
```

4. Open your browser and navigate to `http://localhost:5000`

### Manual Setup (Alternative)

If you prefer to set up manually:

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Download NLTK data:
```python
python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt')"
```

3. The ML model will be automatically trained on first run if it doesn't exist.

## ML Model

The system uses a Random Forest classifier trained on service request data to predict priority levels:
- **High Priority** (🔴): Urgent issues requiring immediate attention
- **Medium Priority** (🟡): Important but not urgent
- **Low Priority** (🟢): Standard requests

### Using Your Own Dataset

The system can be trained on your own dataset instead of the default sample data. Here's how:

#### 1. Prepare Your Dataset

Your dataset should be in CSV, Excel (.xlsx/.xls), or JSON format with the following columns:
- **category**: The type of service request (e.g., "Streetlight issue", "Waste collection")
- **description**: The detailed description of the request
- **location**: The location/address of the request (optional but recommended)
- **priority**: The priority level ("High", "Medium", or "Low")

**Example CSV format:**
```csv
category,description,location,priority
Streetlight issue,Broken streetlight causing safety concerns,Main Street,High
Waste collection,Garbage bin is full,Park Avenue,Medium
Road repair,Small pothole on side street,Elm Street,Low
```

**Note:** If your dataset uses different column names, you can map them in `app.py`:
```python
COLUMN_MAPPING = {
    'Category': 'category',
    'Description': 'description',
    'Location': 'location',
    'Priority': 'priority'
}
```

#### 2. Set the Dataset Path

**Option A: Environment Variable (Recommended)**
```bash
# Windows
set DATASET_PATH=path\to\your\dataset.csv
python app.py

# Linux/Mac
export DATASET_PATH=path/to/your/dataset.csv
python app.py
```

**Option B: Edit app.py**
```python
DATASET_PATH = 'path/to/your/dataset.csv'  # Change this line
```

#### 3. Train the Model

The model will automatically train on your dataset when you first run the application. If you want to retrain with a new dataset:

**Via API:**
```bash
curl -X POST http://localhost:5000/admin/retrain_model \
  -H "Content-Type: application/json" \
  -d '{"dataset_path": "path/to/your/dataset.csv"}'
```

**Via Python:**
```python
from ml_model import MLPriorityPredictor

predictor = MLPriorityPredictor(dataset_path='your_dataset.csv')
predictor.retrain_with_dataset()
```

#### 4. Dataset Requirements

- **Minimum records**: At least 20-30 records recommended for good performance
- **Priority distribution**: Try to have examples of all three priority levels
- **Data quality**: Ensure descriptions are meaningful and categories are consistent
- **Priority values**: Must be "High", "Medium", or "Low" (case-insensitive)

A sample dataset template (`dataset_template.csv`) is included in the project root for reference.

## KRR Rules Engine

Rule-based system that provides advisory recommendations based on:
- Request category
- Description keywords
- Location patterns
- Time of submission

## Categories Supported

- Waste collection
- Streetlight issue
- Road repair
- Noise complaint
- Water service issue
- Graffiti removal
- Others

