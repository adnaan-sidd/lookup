"""
Flask routes for phone number validation
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for, send_file, jsonify
from werkzeug.utils import secure_filename
import os
from app.forms import SingleNumberForm, BulkUploadForm
from app.utils import validate_number, bulk_validate, export_results_to_csv
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
main = Blueprint('main', __name__)

@main.route('/', methods=['GET', 'POST'])
def index():
    """Home page with single number validation form"""
    form = SingleNumberForm()
    result = None
    
    if request.method == 'POST':
        logger.info(f"POST request received. Form data: {request.form}")
        logger.info(f"Form errors: {form.errors}")
        logger.info(f"Form validate_on_submit: {form.validate_on_submit()}")
    
    if form.validate_on_submit():
        phone_number = form.phone_number.data.strip()
        logger.info(f"Validating phone number: {phone_number}")
        try:
            result = validate_number(phone_number)
            flash('Number validation completed!', 'success')
        except Exception as e:
            flash(f'Validation error: {str(e)}', 'error')
            logger.error(f"Single validation error: {str(e)}")
    
    return render_template('index.html', form=form, result=result)

@main.route('/bulk', methods=['GET', 'POST'])
def bulk():
    """Bulk validation page with CSV upload"""
    form = BulkUploadForm()
    results = None
    
    if form.validate_on_submit():
        try:
            # Save uploaded file
            file = form.csv_file.data
            filename = secure_filename(file.filename)
            file_path = os.path.join('uploads', filename)
            file.save(file_path)
            
            # Validate numbers
            results = bulk_validate(file_path)
            
            # Clean up uploaded file
            os.remove(file_path)
            
            flash(f'Bulk validation completed! Processed {len(results)} numbers.', 'success')
            
        except Exception as e:
            flash(f'Bulk validation error: {str(e)}', 'error')
            logger.error(f"Bulk validation error: {str(e)}")
    
    return render_template('bulk.html', form=form, results=results)

@main.route('/download_results')
def download_results():
    """Download validation results as CSV"""
    try:
        # Get results from session or request args
        # For simplicity, we'll recreate results from request args
        # In a real app, you'd store results in session or database
        
        # This is a placeholder - in practice you'd need to store results
        # and retrieve them here
        flash('Results download not implemented in this demo', 'info')
        return redirect(url_for('main.bulk'))
        
    except Exception as e:
        flash(f'Download error: {str(e)}', 'error')
        return redirect(url_for('main.bulk'))

@main.route('/api/validate/<phone_number>')
def api_validate(phone_number):
    """API endpoint for phone number validation"""
    try:
        result = validate_number(phone_number)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main.route('/test')
def test():
    """Test route to verify the app is working"""
    return jsonify({
        'status': 'success',
        'message': 'App is running correctly',
        'csrf_enabled': True
    })