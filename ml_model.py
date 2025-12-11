import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
import joblib
import os
import re
from datetime import datetime

class MLPriorityPredictor:
    def __init__(self, dataset_path=None, column_mapping=None):
        """
        Initialize ML Priority Predictor
        
        Args:
            dataset_path: Path to dataset file (CSV, Excel, or JSON)
            column_mapping: Dict mapping dataset columns to expected columns
                          {'category': 'Category', 'description': 'Description', 
                           'location': 'Location', 'priority': 'Priority'}
        """
        self.model = None
        self.tfidf_vectorizer = None
        self.category_encoder = None
        self.model_path = 'models/priority_model.joblib'
        self.vectorizer_path = 'models/tfidf_vectorizer.joblib'
        self.encoder_path = 'models/category_encoder.joblib'
        self.dataset_path = dataset_path
        self.column_mapping = column_mapping or {}
        
        # Create models directory
        os.makedirs('models', exist_ok=True)
        
        # Priority keywords for explanation
        self.priority_keywords = {
            'High': ['emergency', 'urgent', 'dangerous', 'danger', 'hazard', 'hazardous', 
                    'broken', 'damage', 'damaged', 'critical', 'immediate', 'safety',
                    'unsafe', 'accident', 'injured', 'fire', 'flood', 'overflowing',
                    'blocked', 'blocking', 'dark', 'no light', 'no lights'],
            'Medium': ['issue', 'problem', 'needs', 'repair', 'maintenance', 'not working',
                      'malfunction', 'concern', 'complaint', 'disturbance'],
            'Low': ['request', 'inquiry', 'question', 'information', 'general']
        }
    
    def load_dataset(self, file_path=None):
        """
        Load dataset from file (CSV, Excel, or JSON)
        
        Args:
            file_path: Path to dataset file. If None, uses self.dataset_path
            
        Returns:
            DataFrame with columns: category, description, location, priority
        """
        if file_path is None:
            file_path = self.dataset_path
        
        if file_path is None or not os.path.exists(file_path):
            print(f"Dataset file not found: {file_path}. Using sample data.")
            return None
        
        try:
            # Determine file type and load
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.csv':
                df = pd.read_csv(file_path)
            elif file_ext in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path)
            elif file_ext == '.json':
                df = pd.read_json(file_path)
            else:
                print(f"Unsupported file format: {file_ext}. Using sample data.")
                return None
            
            # Apply column mapping if provided
            if self.column_mapping:
                df = df.rename(columns=self.column_mapping)
            
            # Auto-detect column names (case-insensitive)
            df.columns = df.columns.str.strip()
            column_map = {}
            
            # Try to find category column
            for col in df.columns:
                if 'category' in col.lower() or 'type' in col.lower():
                    column_map['category'] = col
                    break
            
            # Try to find description column
            for col in df.columns:
                if 'description' in col.lower() or 'desc' in col.lower() or 'details' in col.lower():
                    column_map['description'] = col
                    break
            
            # Try to find location column
            for col in df.columns:
                if 'location' in col.lower() or 'address' in col.lower() or 'barangay' in col.lower():
                    column_map['location'] = col
                    break
            
            # Try to find priority column
            for col in df.columns:
                if 'priority' in col.lower() or 'label' in col.lower() or 'class' in col.lower():
                    column_map['priority'] = col
                    break
            
            # Rename columns if mapping found
            if column_map:
                df = df.rename(columns={v: k for k, v in column_map.items()})
            
            # Validate required columns
            required_cols = ['category', 'description', 'priority']
            missing_cols = [col for col in required_cols if col not in df.columns]
            
            if missing_cols:
                print(f"Missing required columns: {missing_cols}")
                print(f"Available columns: {list(df.columns)}")
                print("Using sample data instead.")
                return None
            
            # Clean data
            df = df.dropna(subset=required_cols)
            
            # Normalize priority values
            if 'priority' in df.columns:
                df['priority'] = df['priority'].astype(str).str.strip()
                df['priority'] = df['priority'].str.title()
                # Map common variations
                priority_map = {
                    'High': 'High', 'H': 'High', '1': 'High', 'Urgent': 'High',
                    'Medium': 'Medium', 'M': 'Medium', '2': 'Medium', 'Normal': 'Medium',
                    'Low': 'Low', 'L': 'Low', '3': 'Low', 'Minor': 'Low'
                }
                df['priority'] = df['priority'].map(priority_map).fillna(df['priority'])
                
                # Filter out invalid priority values (only keep High, Medium, Low)
                valid_priorities = ['High', 'Medium', 'Low']
                invalid_count = len(df[~df['priority'].isin(valid_priorities)])
                if invalid_count > 0:
                    print(f"Warning: {invalid_count} records with invalid priority values will be removed.")
                df = df[df['priority'].isin(valid_priorities)]
            
            # Add location if missing (use empty string)
            if 'location' not in df.columns:
                df['location'] = ''
            
            # Select only required columns
            df = df[required_cols + ['location']]
            
            # Final validation - ensure we have data
            if len(df) == 0:
                print("Error: No valid records found in dataset after cleaning.")
                return None
            
            print(f"Dataset loaded successfully: {len(df)} records")
            print(f"Priority distribution:\n{df['priority'].value_counts()}")
            
            return df
            
        except Exception as e:
            print(f"Error loading dataset: {str(e)}")
            print("Using sample data instead.")
            return None
    
    def generate_sample_data(self):
        """Generate sample training data based on common service request patterns"""
        sample_data = []
        
        # High priority examples
        high_priority_examples = [
            ('Streetlight issue', 'Streetlight is broken and area is completely dark, very dangerous at night', 'Main Street'),
            ('Waste collection', 'Garbage is overflowing and blocking the road, creating health hazard', 'Park Avenue'),
            ('Road repair', 'Large pothole causing accidents, immediate repair needed', 'Highway 1'),
            ('Water service issue', 'Water pipe burst flooding the street, urgent attention required', 'Oak Street'),
            ('Streetlight issue', 'No lights working, dangerous area for pedestrians', 'Elm Street'),
            ('Waste collection', 'Trash overflowing everywhere, health emergency', 'Maple Drive'),
        ]
        
        # Medium priority examples
        medium_priority_examples = [
            ('Road repair', 'Road needs repair, some potholes present', 'Second Street'),
            ('Streetlight issue', 'Streetlight flickering, needs maintenance', 'Third Avenue'),
            ('Waste collection', 'Garbage collection missed this week', 'Fourth Street'),
            ('Noise complaint', 'Loud noise from construction site', 'Fifth Avenue'),
            ('Water service issue', 'Water pressure is low', 'Sixth Street'),
            ('Graffiti removal', 'Graffiti on public wall needs removal', 'Seventh Avenue'),
        ]
        
        # Low priority examples
        low_priority_examples = [
            ('Graffiti removal', 'Small graffiti on wall', 'Eighth Street'),
            ('Noise complaint', 'Minor noise from neighbor', 'Ninth Avenue'),
            ('Others', 'General inquiry about services', 'Tenth Street'),
            ('Waste collection', 'Request for additional bin', 'Eleventh Avenue'),
            ('Road repair', 'Minor road maintenance needed', 'Twelfth Street'),
        ]
        
        for category, description, location in high_priority_examples:
            sample_data.append({
                'category': category,
                'description': description,
                'location': location,
                'priority': 'High'
            })
        
        for category, description, location in medium_priority_examples:
            sample_data.append({
                'category': category,
                'description': description,
                'location': location,
                'priority': 'Medium'
            })
        
        for category, description, location in low_priority_examples:
            sample_data.append({
                'category': category,
                'description': description,
                'location': location,
                'priority': 'Low'
            })
        
        # Add more variations
        for _ in range(50):
            sample_data.append({
                'category': np.random.choice(['Waste collection', 'Streetlight issue', 'Road repair', 
                                            'Noise complaint', 'Water service issue', 'Graffiti removal', 'Others']),
                'description': self._generate_random_description(),
                'location': f"Street {np.random.randint(1, 100)}",
                'priority': np.random.choice(['High', 'Medium', 'Low'], p=[0.3, 0.4, 0.3])
            })
        
        return pd.DataFrame(sample_data)
    
    def _generate_random_description(self):
        """Generate random description for training data"""
        templates = [
            "Issue with {item}",
            "{item} needs attention",
            "Problem with {item}",
            "{item} is broken",
            "Request for {item} service"
        ]
        items = ['streetlight', 'garbage', 'road', 'water', 'noise', 'graffiti']
        return np.random.choice(templates).format(item=np.random.choice(items))
    
    def prepare_features(self, df):
        """Prepare features for ML model"""
        # Combine category and description for text features
        df['text'] = df['category'] + ' ' + df['description']
        
        # TF-IDF vectorization
        if self.tfidf_vectorizer is None:
            self.tfidf_vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
            text_features = self.tfidf_vectorizer.fit_transform(df['text'])
        else:
            text_features = self.tfidf_vectorizer.transform(df['text'])
        
        # Category encoding
        if self.category_encoder is None:
            self.category_encoder = LabelEncoder()
            category_encoded = self.category_encoder.fit_transform(df['category'])
        else:
            category_encoded = self.category_encoder.transform(df['category'])
        
        # Combine features
        from scipy.sparse import hstack
        features = hstack([text_features, category_encoded.reshape(-1, 1)])
        
        return features
    
    def train_model(self, df=None, dataset_path=None):
        """
        Train the ML model
        
        Args:
            df: DataFrame with training data. If None, tries to load from dataset_path or self.dataset_path
            dataset_path: Path to dataset file (overrides self.dataset_path)
        """
        if df is None:
            # Try to load from dataset
            if dataset_path:
                df = self.load_dataset(dataset_path)
            elif self.dataset_path:
                df = self.load_dataset(self.dataset_path)
            
            # Fall back to sample data if dataset loading failed
            if df is None or len(df) == 0:
                print("No dataset available. Generating sample data...")
                df = self.generate_sample_data()
        
        # Prepare features
        X = self.prepare_features(df)
        y = df['priority'].values
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Train model
        self.model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10)
        self.model.fit(X_train, y_train)
        
        # Save model
        joblib.dump(self.model, self.model_path)
        joblib.dump(self.tfidf_vectorizer, self.vectorizer_path)
        joblib.dump(self.category_encoder, self.encoder_path)
        
        # Calculate accuracy
        accuracy = self.model.score(X_test, y_test)
        print(f"Model trained with accuracy: {accuracy:.2f}")
        
        return accuracy
    
    def load_model(self):
        """Load trained model"""
        if os.path.exists(self.model_path):
            self.model = joblib.load(self.model_path)
            self.tfidf_vectorizer = joblib.load(self.vectorizer_path)
            self.category_encoder = joblib.load(self.encoder_path)
            return True
        return False
    
    def initialize_model(self, force_retrain=False):
        """
        Initialize model - train if not exists, otherwise load
        
        Args:
            force_retrain: If True, retrain model even if it exists
        """
        if force_retrain or not self.load_model():
            print("Training new model...")
            self.train_model()
        else:
            print("Model loaded successfully")
    
    def retrain_with_dataset(self, dataset_path=None):
        """
        Retrain the model with a new dataset
        
        Args:
            dataset_path: Path to new dataset file
        """
        print("Retraining model with dataset...")
        if dataset_path:
            self.dataset_path = dataset_path
        accuracy = self.train_model()
        print(f"Model retrained successfully with accuracy: {accuracy:.2f}")
        return accuracy
    
    def predict_priority(self, category, description, location):
        """Predict priority for a new request"""
        if self.model is None:
            self.initialize_model()
        
        # Prepare input
        text = f"{category} {description}"
        text_features = self.tfidf_vectorizer.transform([text])
        
        try:
            category_encoded = self.category_encoder.transform([category])[0]
        except ValueError:
            # If category not in training data, use a default encoding
            category_encoded = 0
        
        from scipy.sparse import hstack
        features = hstack([text_features, [[category_encoded]]])
        
        # Predict
        prediction = self.model.predict(features)[0]
        probabilities = self.model.predict_proba(features)[0]
        confidence = max(probabilities)
        
        # Get explanation
        explanation = self._generate_explanation(category, description, prediction, confidence)
        
        return {
            'priority': prediction,
            'confidence': float(confidence),
            'explanation': explanation
        }
    
    def _generate_explanation(self, category, description, priority, confidence):
        """Generate explanation for the prediction"""
        description_lower = description.lower()
        
        # Find matching keywords
        matched_keywords = []
        for keyword in self.priority_keywords.get(priority, []):
            if keyword in description_lower:
                matched_keywords.append(keyword)
        
        explanation_parts = []
        
        if matched_keywords:
            explanation_parts.append(f"Keywords detected: {', '.join(matched_keywords[:3])}")
        
        explanation_parts.append(f"Category '{category}' typically indicates {priority.lower()} priority")
        explanation_parts.append(f"Confidence: {confidence:.2%}")
        
        return ". ".join(explanation_parts)


