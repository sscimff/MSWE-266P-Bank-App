from flask import Blueprint, render_template, flash, redirect, url_for
from db import Account, db
from transaction_form import DepositForm, WithdrawForm

transaction = Blueprint("transaction", __name__, static_folder="static",
                        template_folder="templates/transaction")


@transaction.route("/")
def index():
    return render_template('index.html')


@transaction.route("/show")
def show():
    # TODO: Check current user
    account = db.get_or_404(Account, 1)
    return render_template("show_balance.html", account=account)


@transaction.route('/deposit', methods=['GET', 'POST'])
def deposit():
    # Check auth
    form = DepositForm()
    if form.validate_on_submit():
        amount = form.amount.data
        # TODO: Check current user
        account = Account.query.first()
        if account:
            account.balance += float(amount)
            db.session.commit()
            flash(f'Successfully deposited ${amount:.2f}', 'success')
            return redirect(url_for('transaction.show'))
        else:
            flash('Account not found.', 'danger')
    return render_template('deposit.html', form=form)


@transaction.route('/withdraw', methods=['GET', 'POST'])
def withdraw():
    # Check auth
    form = WithdrawForm()
    if form.validate_on_submit():
        amount = form.amount.data
        # TODO: Check current user
        account = Account.query.first()
        if account:
            # Valid
            if account.balance >= amount:
                account.balance -= float(amount)
                db.session.commit()
                flash(f'Successfully withdrew ${amount:.2f}', 'success')
                return redirect(url_for('transaction.show'))
            # Invalid
            else:
                flash('Insufficient funds.', 'danger')
        else:
            flash('Account not found.', 'danger')
    return render_template('withdraw.html', form=form)
