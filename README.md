# Phone Number Validator Web App

A comprehensive Flask web application for validating phone numbers using multiple APIs and services. The app provides both single number validation and bulk CSV validation with a clean Bootstrap interface.

## Features

- **Single Number Validation**: Validate individual phone numbers with detailed information
- **Bulk CSV Validation**: Upload CSV files with multiple phone numbers for batch processing
- **Multiple Validation Services**:
  - **libphonenumber**: Format validation and country detection
  - **NumVerify API**: Carrier information and location data
  - **Twilio Lookup API**: Line type and fraud detection
- **Modern UI**: Clean Bootstrap interface with responsive design
- **API Endpoint**: RESTful API for programmatic access
- **Export Results**: Download validation results as CSV
- **Deployment Ready**: Configured for Heroku and Render deployment

## Project Structure

```
phone-validator-app/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── routes.py            # Flask routes and views
│   ├── utils.py             # Validation utilities and API calls
│   ├── forms.py             # WTForms for form handling
│   ├── templates/
│   │   ├── base.html        # Base template with Bootstrap
│   │   ├── index.html       # Single validation page
│   │   └── bulk.html        # Bulk validation page
│   └── static/
│       ├── css/style.css    # Custom CSS styles
│       └── js/main.js       # JavaScript functionality
├── tests/
│   ├── test_utils.py        # Unit tests for utilities
│   └── test_routes.py       # Unit tests for routes
├── uploads/                 # Temporary file storage
├── .env                     # Environment variables
├── config.py               # Configuration settings
├── requirements.txt        # Python dependencies
├── run.py                  # Application entry point
├── Procfile               # Heroku deployment
└── README.md              # This file
```

## Setup Instructions

### 1. Environment Setup

#### Using Conda (Recommended)
```bash
# Create a new conda environment
conda create -n phone-validator python=3.9

# Activate the environment
conda activate phone-validator

# Navigate to project directory
cd phone-validator-app
```

#### Using Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Navigate to project directory
cd phone-validator-app
```

### 2. Install Dependencies

```bash
# Install required packages
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy the `.env` file and update with your API keys:

```bash
cp .env .env.local
```

Edit `.env.local` with your actual API keys:

```env
# Flask Configuration
SECRET_KEY=your-super-secret-key-here

# NumVerify API (https://numverify.com/)
NUMVERIFY_API_KEY=your_numverify_api_key_here

# Twilio API (https://www.twilio.com/)
TWILIO_SID=your_twilio_account_sid_here
TWILIO_AUTH_TOKEN=your_twilio_auth_token_here
```

### 4. Run the Application

```bash
# Start the development server
python run.py
```

The application will be available at `http://localhost:5000`

## API Keys Setup

### NumVerify API
1. Visit [NumVerify](https://numverify.com/)
2. Sign up for a free account
3. Get your API key from the dashboard
4. Add it to your `.env` file

### Twilio API
1. Visit [Twilio Console](https://console.twilio.com/)
2. Sign up for a free account
3. Get your Account SID and Auth Token
4. Add them to your `.env` file

## Usage

### Single Number Validation
1. Navigate to the home page
2. Enter a phone number with country code (e.g., +1234567890)
3. Click "Validate Number"
4. View detailed validation results

### Bulk Validation
1. Navigate to the bulk validation page
2. Prepare a CSV file with phone numbers in the first column
3. Upload the CSV file
4. View results in a table format
5. Copy or download results as CSV

### CSV Format Example
```csv
phone_number
+1234567890
+44123456789
+33123456789
+49123456789
+86123456789
```

## API Endpoints

### Validate Single Number
```
GET /api/validate/<phone_number>
```

Example:
```bash
curl http://localhost:5000/api/validate/+1234567890
```

Response:
```json
{
  "original_number": "+1234567890",
  "formatted_number": "+1 234-567-890",
  "country": "US",
  "valid_lib": true,
  "valid_numverify": true,
  "carrier": "Verizon",
  "location": "United States, New York",
  "line_type": "mobile",
  "fraud_risk": "Low",
  "disposable": false,
  "errors": []
}
```

## Testing

Run the test suite:

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=app

# Run specific test file
python -m pytest tests/test_utils.py
```

## Deployment

### Heroku Deployment

1. **Install Heroku CLI** and login:
```bash
heroku login
```

2. **Create Heroku app**:
```bash
heroku create your-app-name
```

3. **Set environment variables**:
```bash
heroku config:set SECRET_KEY=your-secret-key
heroku config:set NUMVERIFY_API_KEY=your-numverify-key
heroku config:set TWILIO_SID=your-twilio-sid
heroku config:set TWILIO_AUTH_TOKEN=your-twilio-token
```

4. **Deploy**:
```bash
git add .
git commit -m "Initial deployment"
git push heroku main
```

5. **Open app**:
```bash
heroku open
```

### Render Deployment

1. **Connect your GitHub repository** to Render
2. **Create a new Web Service**
3. **Configure build command**: `pip install -r requirements.txt`
4. **Configure start command**: `gunicorn run:app`
5. **Add environment variables** in Render dashboard
6. **Deploy**

## Configuration

The application uses environment-based configuration. Key settings:

- `SECRET_KEY`: Flask secret key for sessions
- `MAX_CONTENT_LENGTH`: Maximum file upload size (default: 16MB)
- `UPLOAD_FOLDER`: Directory for temporary file storage
- `MAX_BULK_NUMBERS`: Maximum numbers per bulk validation (default: 1000)

## Error Handling

The application includes comprehensive error handling:

- **API Failures**: Graceful degradation when external APIs are unavailable
- **File Upload Errors**: Validation of file types and sizes
- **Form Validation**: Client and server-side validation
- **Rate Limiting**: Built-in protection against abuse

## Security Features

- **CSRF Protection**: All forms protected against CSRF attacks
- **File Type Validation**: Only CSV files allowed for upload
- **Input Sanitization**: All user inputs are sanitized
- **Environment Variables**: Sensitive data stored in environment variables

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For issues and questions:
1. Check the documentation
2. Search existing issues
3. Create a new issue with detailed information

## Changelog

### Version 1.0.0
- Initial release
- Single number validation
- Bulk CSV validation
- Multiple API integration
- Bootstrap UI
- Deployment configuration