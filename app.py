from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import json
from ml_model import MLPriorityPredictor
from krr_engine import KRREngine

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///service_requests.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Dataset configuration - set via environment variable or default path
# If vehicle_dataset.csv exists, it will be used; otherwise falls back to sample data
DATASET_PATH = os.environ.get('DATASET_PATH', 'vehicle_dataset.csv' if os.path.exists('vehicle_dataset.csv') else 'dataset.csv')
COLUMN_MAPPING = None  # Set if your dataset has different column names
# Example: COLUMN_MAPPING = {'Category': 'category', 'Description': 'description', 'Priority': 'priority', 'Location': 'location'}

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)

# Initialize ML and KRR components
# ML predictor will use dataset if available, otherwise fall back to sample data
ml_predictor = MLPriorityPredictor(dataset_path=DATASET_PATH, column_mapping=COLUMN_MAPPING)
krr_engine = KRREngine()

# Database Models
class ServiceRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    location = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    photo_path = db.Column(db.String(200))
    ml_priority = db.Column(db.String(20), nullable=False)
    ml_confidence = db.Column(db.Float)
    ml_explanation = db.Column(db.Text)
    krr_advisory = db.Column(db.Text)
    status = db.Column(db.String(20), default='Pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'location': self.location,
            'category': self.category,
            'description': self.description,
            'photo_path': self.photo_path,
            'ml_priority': self.ml_priority,
            'ml_confidence': self.ml_confidence,
            'ml_explanation': self.ml_explanation,
            'krr_advisory': self.krr_advisory,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# Routes
@app.route('/')
def index():
    """Dashboard/Home page"""
    total_requests = ServiceRequest.query.count()
    pending = ServiceRequest.query.filter_by(status='Pending').count()
    in_progress = ServiceRequest.query.filter_by(status='In-Progress').count()
    completed = ServiceRequest.query.filter_by(status='Completed').count()
    
    # Category counts for graph
    categories = db.session.query(
        ServiceRequest.category,
        db.func.count(ServiceRequest.id).label('count')
    ).group_by(ServiceRequest.category).all()
    
    category_data = {cat: count for cat, count in categories}
    
    return render_template('index.html',
                         total_requests=total_requests,
                         pending=pending,
                         in_progress=in_progress,
                         completed=completed,
                         category_data=category_data)

@app.route('/submit', methods=['GET', 'POST'])
def submit_request():
    """Submit a service request"""
    if request.method == 'POST':
        data = request.form
        
        # Get form data
        name = data.get('name', '')
        location = data.get('location', '')
        category = data.get('category', '')
        description = data.get('description', '')
        
        # Handle file upload
        photo_path = None
        if 'photo' in request.files:
            file = request.files['photo']
            if file and file.filename:
                filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                photo_path = f"uploads/{filename}"
        
        # ML Prediction
        ml_result = ml_predictor.predict_priority(category, description, location)
        
        # KRR Advisory
        krr_advisory = krr_engine.get_advisory(category, description, location)
        
        # Create service request
        request_obj = ServiceRequest(
            name=name,
            location=location,
            category=category,
            description=description,
            photo_path=photo_path,
            ml_priority=ml_result['priority'],
            ml_confidence=ml_result['confidence'],
            ml_explanation=ml_result['explanation'],
            krr_advisory=krr_advisory
        )
        
        db.session.add(request_obj)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'request_id': request_obj.id,
            'ml_priority': ml_result['priority'],
            'ml_confidence': ml_result['confidence'],
            'ml_explanation': ml_result['explanation'],
            'krr_advisory': krr_advisory
        })
    
    return render_template('submit.html')

@app.route('/requests')
def view_requests():
    """View all service requests"""
    # Get filter parameters
    priority_filter = request.args.get('priority', '')
    category_filter = request.args.get('category', '')
    status_filter = request.args.get('status', '')
    sort_by = request.args.get('sort', 'date')
    
    # Build query
    query = ServiceRequest.query
    
    if priority_filter:
        query = query.filter_by(ml_priority=priority_filter)
    if category_filter:
        query = query.filter_by(category=category_filter)
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    # Sort
    if sort_by == 'priority':
        query = query.order_by(ServiceRequest.ml_priority.desc())
    elif sort_by == 'category':
        query = query.order_by(ServiceRequest.category)
    elif sort_by == 'location':
        query = query.order_by(ServiceRequest.location)
    else:
        query = query.order_by(ServiceRequest.created_at.desc())
    
    requests = query.all()
    
    return render_template('requests.html', requests=requests,
                         priority_filter=priority_filter,
                         category_filter=category_filter,
                         status_filter=status_filter,
                         sort_by=sort_by)

@app.route('/request/<int:request_id>')
def request_details(request_id):
    """View request details"""
    request_obj = ServiceRequest.query.get_or_404(request_id)
    return render_template('details.html', request=request_obj)

@app.route('/request/<int:request_id>/update_status', methods=['POST'])
def update_status(request_id):
    """Update request status"""
    request_obj = ServiceRequest.query.get_or_404(request_id)
    new_status = request.json.get('status')
    
    if new_status in ['Pending', 'In-Progress', 'Completed']:
        request_obj.status = new_status
        db.session.commit()
        return jsonify({'success': True})
    
    return jsonify({'success': False, 'error': 'Invalid status'}), 400

@app.route('/admin')
def admin_panel():
    """Admin panel"""
    # Get filter parameters
    priority_filter = request.args.get('priority', '')
    category_filter = request.args.get('category', '')
    today_only = request.args.get('today', '') == 'true'
    sort_by = request.args.get('sort', 'priority')
    
    # Build query
    query = ServiceRequest.query
    
    if priority_filter:
        query = query.filter_by(ml_priority=priority_filter)
    if category_filter:
        query = query.filter_by(category=category_filter)
    if today_only:
        today = datetime.now().date()
        query = query.filter(db.func.date(ServiceRequest.created_at) == today)
    
    # Sort
    if sort_by == 'priority':
        query = query.order_by(ServiceRequest.ml_priority.desc(), ServiceRequest.ml_confidence.desc())
    elif sort_by == 'category':
        query = query.order_by(ServiceRequest.category)
    elif sort_by == 'location':
        query = query.order_by(ServiceRequest.location)
    else:
        query = query.order_by(ServiceRequest.created_at.desc())
    
    requests = query.all()
    
    # Statistics for report
    total = len(requests)
    high_priority = sum(1 for r in requests if r.ml_priority == 'High')
    medium_priority = sum(1 for r in requests if r.ml_priority == 'Medium')
    low_priority = sum(1 for r in requests if r.ml_priority == 'Low')
    
    return render_template('admin.html', 
                         requests=requests,
                         priority_filter=priority_filter,
                         category_filter=category_filter,
                         today_only=today_only,
                         sort_by=sort_by,
                         stats={'total': total, 'high': high_priority, 'medium': medium_priority, 'low': low_priority})

@app.route('/admin/override_priority/<int:request_id>', methods=['POST'])
def override_priority(request_id):
    """Manually override ML priority"""
    request_obj = ServiceRequest.query.get_or_404(request_id)
    new_priority = request.json.get('priority')
    
    if new_priority in ['High', 'Medium', 'Low']:
        request_obj.ml_priority = new_priority
        request_obj.ml_explanation = f"Manually overridden by admin. Original: {request_obj.ml_priority}"
        db.session.commit()
        return jsonify({'success': True})
    
    return jsonify({'success': False, 'error': 'Invalid priority'}), 400

@app.route('/api/stats')
def api_stats():
    """API endpoint for statistics"""
    total = ServiceRequest.query.count()
    pending = ServiceRequest.query.filter_by(status='Pending').count()
    in_progress = ServiceRequest.query.filter_by(status='In-Progress').count()
    completed = ServiceRequest.query.filter_by(status='Completed').count()
    
    categories = db.session.query(
        ServiceRequest.category,
        db.func.count(ServiceRequest.id).label('count')
    ).group_by(ServiceRequest.category).all()
    
    return jsonify({
        'total': total,
        'pending': pending,
        'in_progress': in_progress,
        'completed': completed,
        'categories': {cat: count for cat, count in categories}
    })

@app.route('/admin/retrain_model', methods=['POST'])
def retrain_model():
    """Retrain ML model with dataset"""
    try:
        dataset_path = request.json.get('dataset_path') if request.is_json else request.form.get('dataset_path', DATASET_PATH)
        
        if dataset_path and os.path.exists(dataset_path):
            accuracy = ml_predictor.retrain_with_dataset(dataset_path)
            return jsonify({
                'success': True,
                'message': f'Model retrained successfully with accuracy: {accuracy:.2%}',
                'accuracy': accuracy
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Dataset file not found: {dataset_path}'
            }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/admin/model_info')
def model_info():
    """Get information about the current ML model"""
    dataset_status = 'Available' if (ml_predictor.dataset_path and os.path.exists(ml_predictor.dataset_path)) else 'Not available (using sample data)'
    model_status = 'Loaded' if ml_predictor.model is not None else 'Not loaded'
    
    return jsonify({
        'model_status': model_status,
        'dataset_path': ml_predictor.dataset_path or 'Not set',
        'dataset_status': dataset_status,
        'model_files': {
            'model': os.path.exists(ml_predictor.model_path),
            'vectorizer': os.path.exists(ml_predictor.vectorizer_path),
            'encoder': os.path.exists(ml_predictor.encoder_path)
        }
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Initialize ML model (train if needed)
        ml_predictor.initialize_model()
    app.run(debug=True)


