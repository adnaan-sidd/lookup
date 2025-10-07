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
        logger.info(f"CSRF token in form: {form.csrf_token.data if hasattr(form, 'csrf_token') else 'No CSRF token field'}")
        logger.info(f"Request CSRF token: {request.form.get('csrf_token', 'No CSRF token in request')}")
        
        # Handle CSRF token manually if needed
        if not form.validate_on_submit():
            if 'csrf_token' in form.errors:
                flash('CSRF token error. Please try again.', 'error')
                logger.error(f"CSRF token validation failed: {form.errors['csrf_token']}")
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        flash(f'{field}: {error}', 'error')
                        logger.error(f"Form validation error - {field}: {error}")
    
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
    
    if request.method == 'POST':
        # Handle CSRF token manually if needed
        if not form.validate_on_submit():
            if 'csrf_token' in form.errors:
                flash('CSRF token error. Please try again.', 'error')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        flash(f'{field}: {error}', 'error')
    
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
    from flask_wtf.csrf import generate_csrf
    return jsonify({
        'status': 'success',
        'message': 'App is running correctly',
        'csrf_enabled': True,
        'csrf_token': generate_csrf()
    })

@main.route('/csrf-token')
def csrf_token():
    """Get CSRF token for debugging"""
    from flask_wtf.csrf import generate_csrf
    return jsonify({
        'csrf_token': generate_csrf()
    })

@main.route('/test-form', methods=['GET', 'POST'])
def test_form():
    """Test form without CSRF for debugging"""
    if request.method == 'POST':
        phone_number = request.form.get('phone_number', '').strip()
        if phone_number:
            try:
                result = validate_number(phone_number)
                return jsonify({
                    'status': 'success',
                    'result': result
                })
            except Exception as e:
                return jsonify({
                    'status': 'error',
                    'message': str(e)
                }), 500
        else:
            return jsonify({
                'status': 'error',
                'message': 'No phone number provided'
            }), 400
    
    return '''
    <form method="POST">
        <input type="text" name="phone_number" placeholder="Enter phone number" required>
        <button type="submit">Test Validate</button>
    </form>
    '''