from flask_wtf import FlaskForm
from wtforms import DecimalField, SubmitField
from wtforms.validators import DataRequired, NumberRange


class DepositForm(FlaskForm):
    amount = DecimalField('Amount', validators=[DataRequired(), NumberRange(
        min=0.01, message="Amount must be greater than zero.")])
    submit = SubmitField('Deposit')

class WithdrawForm(FlaskForm):
    amount = DecimalField('Amount', validators=[DataRequired(), NumberRange(
        min=0.01, message="Amount must be greater than zero and smaller or equal to your current balance.")])
    submit = SubmitField('Withdraw')
