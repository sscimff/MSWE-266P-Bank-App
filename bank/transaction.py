import io
from datetime import datetime
import re
from flask import Blueprint, render_template, flash, redirect, request, send_file, url_for, session, g
from db import Account, db
from transaction_form import DepositForm, WithdrawForm
from flask_wtf import FlaskForm


bp_transaction = Blueprint("transaction", __name__,
                           template_folder="templates/transaction")


class DummyForm(FlaskForm):
    pass


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
    dummy_form = DummyForm()
    return render_template("show_balance.html", account=account, form=dummy_form)


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


@bp_transaction.route('/save_transaction', methods=['POST'])
def save_transaction():
    if g.user is None:
        return redirect(url_for('user.login'))

    filename = request.form.get('filename')

    safe_filename = re.sub(r'[^a-zA-Z0-9_\-]', '_', filename)
    safe_filename = f"{safe_filename}_{
        datetime.now().strftime('%Y%m%d%H%M%S')}.txt"

    data = f"Current Balance: ${g.user.balance:.2f}"

    try:
        file_content = io.BytesIO()
        file_content.write(data.encode('utf-8'))
        file_content.seek(0)

        return send_file(
            file_content,
            as_attachment=True,
            download_name=filename,
            mimetype='text/plain'
        )
    except Exception as e:
        flash(f'Error saving transaction history: {str(e)}', 'danger')

    return redirect(url_for('transaction.show'))
