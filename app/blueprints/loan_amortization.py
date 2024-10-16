from flask import Blueprint, render_template, request, url_for, redirect, flash
from app.db_connect import get_db
from app.functions import calculate_amortization

loan_amortization = Blueprint('loan_amortization', __name__)


@loan_amortization.route('/loan', methods=['GET', 'POST'])
def loan():
    db = get_db()
    cursor = db.cursor()

    # Handle POST request to add a new loan
    if request.method == 'POST':
        loan_amount = request.form['loan_amount']
        term_years = request.form['term_years']
        interest_rate = request.form['interest_rate']

        # Calculate the monthly payment using the calculate_amortization function
        monthly_payment = calculate_amortization(loan_amount, term_years, interest_rate)

        # Insert the new loan info into the database
        cursor.execute('INSERT INTO loan_info (loan_amount, term_years, interest_rate) VALUES (%s, %s, %s)', (loan_amount, term_years, interest_rate))
        db.commit()

        flash('New loan information added successfully!', 'success')
        return redirect(url_for('loan_amortization.loan'))

    # Handle GET request to display all loans
    cursor.execute('SELECT * FROM loan_info')
    all_loans = cursor.fetchall()
    return render_template('loans.html', all_loans=all_loans)


@loan_amortization.route('/update_loan/<int:loan_info_id>', methods=['GET', 'POST'])
def update_loan(loan_info_id):
    db = get_db()
    cursor = db.cursor()

    if request.method == 'POST':
        # Update the loan's details
        loan_amount = request.form['loan_amount']
        term_years = request.form['term_years']
        interest_rate = request.form['interest_rate']

        # Calculate the monthly payment using the calculate_amortization function
        monthly_payment = calculate_amortization(loan_amount, term_years, interest_rate)

        cursor.execute('UPDATE loan_info SET loan_amount = %s, term_years = %s, interest_rate = %s WHERE loan_info_id = %s',
                       (loan_amount, term_years, interest_rate, loan_info_id))
        db.commit()

        flash('Loan updated successfully!', 'success')
        return redirect(url_for('loan_amortization.loan'))

    # GET method: fetch runner's current data for pre-populating the form
    cursor.execute('SELECT * FROM loan_info WHERE loan_info_id = %s', (loan_info_id,))
    current_loan_info = cursor.fetchone()
    return render_template('update_loan.html', current_loan_info=current_loan_info)


@loan_amortization.route('/delete_loan/<int:loan_info_id>', methods=['POST'])
def delete_loan(loan_info_id):
    db = get_db()
    cursor = db.cursor()

    # Delete the runner
    cursor.execute('DELETE FROM loan_info WHERE loan_info_id = %s', (loan_info_id,))
    db.commit()

    flash('Loan info deleted successfully!', 'danger')
    return redirect(url_for('loan_amortization.loan'))
