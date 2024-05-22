from flask import Blueprint, render_template, flash, redirect, url_for, session, g
from db import Account, db
from transaction_form import DepositForm, WithdrawForm

bp_transaction = Blueprint("transaction", __name__,
                           template_folder="templates/transaction")


@bp_transaction.before_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = Account.query.get(user_id)


@bp_transaction.route("/")
def index():
    if g.user is None:
        return redirect(url_for('user.login'))

    account = g.user
    return render_template("index.html", account=account)


@bp_transaction.route("/show")
def show():
    if g.user is None:
        return redirect(url_for('user.login'))

    account = g.user
    return render_template("show_balance.html", account=account)


@bp_transaction.route('/deposit', methods=['GET', 'POST'])
def deposit():
    form = DepositForm()
    account = Account.query.first()

    if form.validate_on_submit():
        amount = form.amount.data
        account.balance += float(amount)
        db.session.commit()
        flash(f'Successfully deposited ${amount:.2f}', 'success')
        return redirect(url_for('transaction.show'))

    return render_template('deposit.html', form=form, account=account)


@bp_transaction.route('/withdraw', methods=['GET', 'POST'])
def withdraw():
    if g.user is None:
        return redirect(url_for('user.login'))

    form = WithdrawForm()
    account = g.user
    if form.validate_on_submit():
        amount = form.amount.data
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
    return render_template('withdraw.html', form=form, account=account)
