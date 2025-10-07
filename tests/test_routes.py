"""
Unit tests for Flask routes
"""

import unittest
import os
import sys
import tempfile
from unittest.mock import patch, MagicMock

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.forms import SingleNumberForm, BulkUploadForm

class TestRoutes(unittest.TestCase):
    """Test cases for Flask routes"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        
        # Create temporary directory for uploads
        self.temp_dir = tempfile.mkdtemp()
        self.app.config['UPLOAD_FOLDER'] = self.temp_dir
    
    def tearDown(self):
        """Clean up after tests"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_index_route_get(self):
        """Test GET request to index route"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Phone Number Validation', response.data)
    
    def test_index_route_post_valid(self):
        """Test POST request to index route with valid data"""
        with patch('app.routes.validate_number') as mock_validate:
            mock_validate.return_value = {
                'original_number': '+1234567890',
                'valid_lib': True,
                'formatted_number': '+1 234-567-890',
                'country': 'US'
            }
            
            response = self.client.post('/', data={
                'phone_number': '+1234567890',
                'csrf_token': 'test_token'
            })
            
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Validation Results', response.data)
    
    def test_index_route_post_invalid(self):
        """Test POST request to index route with invalid data"""
        response = self.client.post('/', data={
            'phone_number': '123',  # Too short
            'csrf_token': 'test_token'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Field must be between 10 and 20 characters long', response.data)
    
    def test_bulk_route_get(self):
        """Test GET request to bulk route"""
        response = self.client.get('/bulk')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Bulk Phone Number Validation', response.data)
    
    def test_bulk_route_post_valid(self):
        """Test POST request to bulk route with valid CSV"""
        # Create a temporary CSV file
        csv_content = "phone_number\n+1234567890\n+44123456789"
        csv_path = os.path.join(self.temp_dir, 'test.csv')
        with open(csv_path, 'w') as f:
            f.write(csv_content)
        
        with patch('app.routes.bulk_validate') as mock_bulk_validate:
            mock_bulk_validate.return_value = [
                {'original_number': '+1234567890', 'valid_lib': True},
                {'original_number': '+44123456789', 'valid_lib': True}
            ]
            
            with open(csv_path, 'rb') as f:
                response = self.client.post('/bulk', data={
                    'csv_file': (f, 'test.csv'),
                    'csrf_token': 'test_token'
                })
            
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Validation Results', response.data)
    
    def test_bulk_route_post_invalid_file(self):
        """Test POST request to bulk route with invalid file type"""
        # Create a temporary text file (not CSV)
        txt_content = "This is not a CSV file"
        txt_path = os.path.join(self.temp_dir, 'test.txt')
        with open(txt_path, 'w') as f:
            f.write(txt_content)
        
        with open(txt_path, 'rb') as f:
            response = self.client.post('/bulk', data={
                'csv_file': (f, 'test.txt'),
                'csrf_token': 'test_token'
            })
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Only CSV files are allowed', response.data)
    
    def test_api_validate_route(self):
        """Test API validation route"""
        with patch('app.routes.validate_number') as mock_validate:
            mock_validate.return_value = {
                'original_number': '+1234567890',
                'valid_lib': True,
                'formatted_number': '+1 234-567-890',
                'country': 'US'
            }
            
            response = self.client.get('/api/validate/+1234567890')
            
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'original_number', response.data)
            self.assertIn(b'+1234567890', response.data)
    
    def test_api_validate_route_error(self):
        """Test API validation route with error"""
        with patch('app.routes.validate_number') as mock_validate:
            mock_validate.side_effect = Exception('Test error')
            
            response = self.client.get('/api/validate/+1234567890')
            
            self.assertEqual(response.status_code, 500)
            self.assertIn(b'error', response.data)

class TestForms(unittest.TestCase):
    """Test cases for WTForms"""
    
    def test_single_number_form_valid(self):
        """Test SingleNumberForm with valid data"""
        form = SingleNumberForm(data={'phone_number': '+1234567890'})
        self.assertTrue(form.validate())
    
    def test_single_number_form_invalid(self):
        """Test SingleNumberForm with invalid data"""
        form = SingleNumberForm(data={'phone_number': '123'})
        self.assertFalse(form.validate())
        self.assertIn('Field must be between 10 and 20 characters long', form.phone_number.errors[0])
    
    def test_bulk_upload_form_valid(self):
        """Test BulkUploadForm with valid data"""
        # This would need a proper file upload test
        form = BulkUploadForm()
        self.assertFalse(form.validate())  # No file uploaded
    
    def test_bulk_upload_form_invalid_extension(self):
        """Test BulkUploadForm with invalid file extension"""
        form = BulkUploadForm()
        # This would need a proper file upload test with wrong extension
        self.assertFalse(form.validate())

if __name__ == '__main__':
    unittest.main()