"""
Unit tests for utils module
"""

import unittest
import os
import sys
from unittest.mock import patch, MagicMock

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils import validate_number, bulk_validate, _call_numverify_api, _call_twilio_lookup

class TestUtils(unittest.TestCase):
    """Test cases for utility functions"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.valid_number = "+1234567890"
        self.invalid_number = "123"
        self.test_csv_path = "test_numbers.csv"
    
    def test_validate_number_valid(self):
        """Test validation of a valid phone number"""
        with patch.dict(os.environ, {'NUMVERIFY_API_KEY': 'test_key', 'TWILIO_SID': 'test_sid', 'TWILIO_AUTH_TOKEN': 'test_token'}):
            with patch('app.utils._call_numverify_api') as mock_numverify:
                with patch('app.utils._call_twilio_lookup') as mock_twilio:
                    mock_numverify.return_value = {
                        'valid': True,
                        'carrier': 'Test Carrier',
                        'country_name': 'United States',
                        'location': 'New York'
                    }
                    mock_twilio.return_value = {
                        'line_type': 'mobile',
                        'fraud_risk': 'Low',
                        'disposable': False
                    }
                    
                    result = validate_number(self.valid_number)
                    
                    self.assertEqual(result['original_number'], self.valid_number)
                    self.assertTrue(result['valid_lib'])
                    self.assertTrue(result['valid_numverify'])
                    self.assertEqual(result['carrier'], 'Test Carrier')
                    self.assertEqual(result['line_type'], 'mobile')
    
    def test_validate_number_invalid(self):
        """Test validation of an invalid phone number"""
        result = validate_number(self.invalid_number)
        
        self.assertEqual(result['original_number'], self.invalid_number)
        self.assertFalse(result['valid_lib'])
        self.assertIn('Invalid number format', result['errors'][0])
    
    def test_validate_number_no_api_keys(self):
        """Test validation without API keys"""
        with patch.dict(os.environ, {}, clear=True):
            result = validate_number(self.valid_number)
            
            self.assertTrue(result['valid_lib'])  # libphonenumber should still work
            self.assertIn('NumVerify API key not configured', result['errors'])
            self.assertIn('Twilio credentials not configured', result['errors'])
    
    @patch('pandas.read_csv')
    def test_bulk_validate(self, mock_read_csv):
        """Test bulk validation with CSV file"""
        # Mock pandas DataFrame
        mock_df = MagicMock()
        mock_df.columns = ['phone_number']
        mock_df.__getitem__.return_value.astype.return_value.tolist.return_value = [
            '+1234567890', '+44123456789'
        ]
        mock_read_csv.return_value = mock_df
        
        with patch('app.utils.validate_number') as mock_validate:
            mock_validate.return_value = {'original_number': 'test', 'valid_lib': True}
            
            results = bulk_validate('test.csv')
            
            self.assertEqual(len(results), 2)
            mock_validate.assert_called()
    
    @patch('requests.get')
    def test_call_numverify_api_success(self, mock_get):
        """Test successful NumVerify API call"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'success': True,
            'valid': True,
            'carrier': 'Test Carrier',
            'country_name': 'United States',
            'location': 'New York'
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = _call_numverify_api('+1234567890', 'test_key')
        
        self.assertIsNotNone(result)
        self.assertTrue(result['valid'])
        self.assertEqual(result['carrier'], 'Test Carrier')
    
    @patch('requests.get')
    def test_call_numverify_api_failure(self, mock_get):
        """Test failed NumVerify API call"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'success': False,
            'error': 'Invalid API key'
        }
        mock_get.return_value = mock_response
        
        result = _call_numverify_api('+1234567890', 'invalid_key')
        
        self.assertIsNone(result)
    
    @patch('app.utils.Client')
    def test_call_twilio_lookup_success(self, mock_client_class):
        """Test successful Twilio Lookup API call"""
        mock_client = MagicMock()
        mock_phone_number = MagicMock()
        mock_phone_number.carrier = {'type': 'mobile'}
        mock_client.lookups.v1.phone_numbers.return_value.fetch.return_value = mock_phone_number
        mock_client_class.return_value = mock_client
        
        result = _call_twilio_lookup('+1234567890', 'test_sid', 'test_token')
        
        self.assertIsNotNone(result)
        self.assertEqual(result['line_type'], 'mobile')
        self.assertEqual(result['fraud_risk'], 'Low')
        self.assertFalse(result['disposable'])
    
    @patch('app.utils.Client')
    def test_call_twilio_lookup_failure(self, mock_client_class):
        """Test failed Twilio Lookup API call"""
        mock_client_class.side_effect = Exception('Invalid credentials')
        
        result = _call_twilio_lookup('+1234567890', 'invalid_sid', 'invalid_token')
        
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()