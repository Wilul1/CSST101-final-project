"""
Setup script to initialize the ML model and download required NLTK data
"""
import nltk
import os

def download_nltk_data():
    """Download required NLTK data"""
    print("Downloading NLTK data...")
    try:
        nltk.download('stopwords', quiet=True)
        nltk.download('punkt', quiet=True)
        print("✓ NLTK data downloaded successfully")
    except Exception as e:
        print(f"Error downloading NLTK data: {e}")

def create_directories():
    """Create necessary directories"""
    directories = ['models', 'static/uploads']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Created directory: {directory}")

def initialize_ml_model():
    """Initialize and train the ML model"""
    print("\nInitializing ML model...")
    try:
        from ml_model import MLPriorityPredictor
        predictor = MLPriorityPredictor()
        predictor.initialize_model()
        print("✓ ML model initialized successfully")
    except Exception as e:
        print(f"Error initializing ML model: {e}")

if __name__ == '__main__':
    print("Setting up ML-Based Priority Ranking System...")
    print("=" * 50)
    
    create_directories()
    download_nltk_data()
    initialize_ml_model()
    
    print("\n" + "=" * 50)
    print("Setup complete! You can now run the application with:")
    print("  python app.py")
    print("=" * 50)


