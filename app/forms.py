"""
WTForms for phone number validation
"""

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length

class SingleNumberForm(FlaskForm):
    """Form for single phone number validation"""
    phone_number = StringField(
        'Phone Number',
        validators=[DataRequired(), Length(min=10, max=20)],
        render_kw={'placeholder': 'Enter phone number (e.g., +1234567890)'}
    )
    submit = SubmitField('Validate Number')

class BulkUploadForm(FlaskForm):
    """Form for bulk CSV upload"""
    csv_file = FileField(
        'CSV File',
        validators=[
            FileRequired(),
            FileAllowed(['csv'], 'Only CSV files are allowed!')
        ]
    )
    submit = SubmitField('Upload and Validate')