from pydantic import BaseModel, EmailStr, Field, ValidationError, validator
import phonenumbers
from phonenumbers import NumberParseException, is_valid_number


class Register(BaseModel):
    email: EmailStr = Field(..., description="The email address of the user.")
    mobile_no: str = Field(..., description="The mobile phone number of the user, including the country code.")
    country_id: int = Field(..., description="The country id.")

    @validator('mobile_no')
    def validate_mobile_no(cls, value):
        try:
            phone_number = phonenumbers.parse(value)
            if not is_valid_number(phone_number):
                raise ValueError('Invalid phone number.')
        except NumberParseException:
            raise ValueError('Invalid phone number format.')
        return value


class AdminRegister(BaseModel):
    email: EmailStr
    mobile_no: str
    user_name: str #constr(min_length=3, max_length=50)
    password: str #constr(min_length=8)

    '''
    @field_validator('passworddd')
    def password_must_contain_digit(cls, value):
        """Ensure the password contains at least one digit."""
        if not any(char.isdigit() for char in value):
            raise ValueError('Password must contain at least one digit')
        return value
    
    @field_validator('mobile_no---')
    def validate_mobile_no(cls, value):
        """Validate phone number for all countries."""
        try:
            # Parse the phone number
            phone_number = phonenumbers.parse(value, None)  # None uses the default region
            
            if not is_valid_number(phone_number):
                raise ValueError("Invalid phone number")
            
            return value
        except NumberParseException:
            raise ValueError("Invalid phone number format")
    '''

