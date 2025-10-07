"""
Utility functions for phone number validation
Integrates with libphonenumber, NumVerify API, and Twilio Lookup API
"""

import phonenumbers
import requests
import pandas as pd
import os
from twilio.rest import Client
from typing import Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_number(number: str) -> Dict:
    """
    Validate a single phone number using multiple services
    
    Args:
        number (str): Phone number to validate
        
    Returns:
        Dict: Validation results from all services
    """
    result = {
        'original_number': number,
        'formatted_number': None,
        'country': None,
        'valid_lib': False,
        'valid_numverify': False,
        'carrier': None,
        'location': None,
        'line_type': None,
        'fraud_risk': None,
        'disposable': None,
        'errors': []
    }
    
    try:
        # Parse with libphonenumber
        parsed_number = phonenumbers.parse(number, None)
        
        if phonenumbers.is_valid_number(parsed_number):
            result['valid_lib'] = True
            result['formatted_number'] = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
            result['country'] = phonenumbers.region_code_for_number(parsed_number)
        else:
            result['errors'].append('Invalid number format according to libphonenumber')
            
    except Exception as e:
        result['errors'].append(f'libphonenumber error: {str(e)}')
    
    # NumVerify API validation
    numverify_api_key = os.getenv('NUMVERIFY_API_KEY')
    if numverify_api_key:
        try:
            numverify_result = _call_numverify_api(number, numverify_api_key)
            if numverify_result:
                result['valid_numverify'] = numverify_result.get('valid', False)
                result['carrier'] = numverify_result.get('carrier', 'Unknown')
                result['location'] = f"{numverify_result.get('country_name', 'Unknown')}, {numverify_result.get('location', 'Unknown')}"
        except Exception as e:
            result['errors'].append(f'NumVerify API error: {str(e)}')
    else:
        result['errors'].append('NumVerify API key not configured')
    
    # Twilio Lookup API
    twilio_sid = os.getenv('TWILIO_SID')
    twilio_auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    
    if twilio_sid and twilio_auth_token:
        try:
            twilio_result = _call_twilio_lookup(number, twilio_sid, twilio_auth_token)
            if twilio_result:
                result['line_type'] = twilio_result.get('line_type', 'Unknown')
                result['fraud_risk'] = twilio_result.get('fraud_risk', 'Unknown')
                result['disposable'] = twilio_result.get('disposable', False)
        except Exception as e:
            result['errors'].append(f'Twilio API error: {str(e)}')
    else:
        result['errors'].append('Twilio credentials not configured')
    
    return result

def _call_numverify_api(number: str, api_key: str) -> Optional[Dict]:
    """Call NumVerify API for phone number validation"""
    try:
        url = f"http://apilayer.net/api/validate"
        params = {
            'access_key': api_key,
            'number': number,
            'format': 1
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        if data.get('success'):
            return data
        else:
            logger.error(f"NumVerify API error: {data.get('error', 'Unknown error')}")
            return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"NumVerify API request failed: {str(e)}")
        return None

def _call_twilio_lookup(number: str, sid: str, auth_token: str) -> Optional[Dict]:
    """Call Twilio Lookup API for phone number information"""
    try:
        client = Client(sid, auth_token)
        
        # Format number for Twilio (remove spaces, add + if needed)
        formatted_number = number.replace(' ', '').replace('-', '')
        if not formatted_number.startswith('+'):
            formatted_number = '+' + formatted_number
        
        phone_number = client.lookups.v1.phone_numbers(formatted_number).fetch()
        
        return {
            'line_type': phone_number.carrier.get('type', 'Unknown') if phone_number.carrier else 'Unknown',
            'fraud_risk': 'Low',  # Twilio doesn't provide fraud risk directly
            'disposable': False   # Twilio doesn't provide disposable info directly
        }
        
    except Exception as e:
        logger.error(f"Twilio Lookup API error: {str(e)}")
        return None

def bulk_validate(file_path: str) -> List[Dict]:
    """
    Validate multiple phone numbers from a CSV file
    
    Args:
        file_path (str): Path to CSV file containing phone numbers
        
    Returns:
        List[Dict]: List of validation results for each number
    """
    results = []
    
    try:
        # Read CSV file
        df = pd.read_csv(file_path)
        
        # Assume first column contains phone numbers
        phone_column = df.columns[0]
        phone_numbers = df[phone_column].astype(str).tolist()
        
        # Validate each number
        for number in phone_numbers:
            if number and number.strip():
                result = validate_number(number.strip())
                results.append(result)
        
        return results
        
    except Exception as e:
        logger.error(f"Bulk validation error: {str(e)}")
        return [{'original_number': 'Error', 'errors': [f'File processing error: {str(e)}']}]

def export_results_to_csv(results: List[Dict], filename: str = 'validation_results.csv') -> str:
    """
    Export validation results to CSV file
    
    Args:
        results (List[Dict]): List of validation results
        filename (str): Output filename
        
    Returns:
        str: Path to exported file
    """
    try:
        # Prepare data for CSV
        csv_data = []
        for result in results:
            csv_data.append({
                'Original Number': result.get('original_number', ''),
                'Formatted Number': result.get('formatted_number', ''),
                'Country': result.get('country', ''),
                'Valid (libphonenumber)': result.get('valid_lib', False),
                'Valid (NumVerify)': result.get('valid_numverify', False),
                'Carrier': result.get('carrier', ''),
                'Location': result.get('location', ''),
                'Line Type': result.get('line_type', ''),
                'Fraud Risk': result.get('fraud_risk', ''),
                'Disposable': result.get('disposable', False),
                'Errors': '; '.join(result.get('errors', []))
            })
        
        # Create DataFrame and export
        df = pd.DataFrame(csv_data)
        output_path = os.path.join('uploads', filename)
        df.to_csv(output_path, index=False)
        
        return output_path
        
    except Exception as e:
        logger.error(f"CSV export error: {str(e)}")
        raise e