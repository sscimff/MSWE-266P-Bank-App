from flask_wtf import FlaskForm
from wtforms import DecimalField, SubmitField
from wtforms.validators import DataRequired, NumberRange, ValidationError
import re


def validate_currency(form, field):
    """
    Validates that the field data fits the currency format:
    - Between 0.01 and 4294967295.99
    - Exactly two decimal places
    """
    pattern = r"^(4294967295\.99|429496729[0-4]\.\d{2}|[0-3]?\d{1,8}\.\d{2})$"
    if not re.match(pattern, str(field.data)):
        raise ValidationError(
            'Invalid amount format. Amount must be between 0.01 and 4294967295.99 with two decimal places.')


class DepositForm(FlaskForm):
    amount = DecimalField('Amount', validators=[DataRequired(), NumberRange(
        min=0.01, message="Amount must be greater than zero.")])
    submit = SubmitField('Deposit')


class WithdrawForm(FlaskForm):
    amount = DecimalField('Amount', validators=[DataRequired(), NumberRange(
        min=0.01, message="Amount must be greater than zero and smaller or equal to your current balance.")])
    submit = SubmitField('Withdraw')
