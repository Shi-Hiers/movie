# create a function that calculates the letter grade based on the number grade
def calculate_grade(number_grade):
    try:
        # Convert number_grade to an integer
        number_grade = int(number_grade)

        if number_grade >= 90:
            letter_grade = "A"
        elif number_grade >= 80:
            letter_grade = "B"
        elif number_grade >= 70:
            letter_grade = "C"
        elif number_grade >= 60:
            letter_grade = "D"
        else:
            letter_grade = "F"

        return letter_grade
    except ValueError:
        # Handle the case where conversion fails (e.g., if input is not a valid number)
        return "Invalid grade input"


# create a function that calculates the loan amortization
def calculate_amortization(loan_amount, term_years, interest_rate):
    # Convert inputs to numeric types (float for loan_amount and interest_rate, int for term_years)
    loan_amount = float(loan_amount)
    term_years = int(term_years)
    interest_rate = float(interest_rate)

    # Calculate the monthly interest rate
    monthly_interest_rate = interest_rate / 12 / 100

    # Calculate the number of payments (in months)
    number_of_payments = term_years * 12

    # Calculate the monthly payment using the amortization formula
    monthly_payment = loan_amount * monthly_interest_rate / (1 - (1 + monthly_interest_rate) ** -number_of_payments)

    return monthly_payment


# Test cases for validation

if __name__ == "__main__":
    # Test calculate_grade function with different number grades
    print("Testing calculate_grade function:")
    print(f"Grade for 95: {calculate_grade(95)}")  # Expected output: A
    print(f"Grade for 85: {calculate_grade(85)}")  # Expected output: B
    print(f"Grade for 75: {calculate_grade(75)}")  # Expected output: C
    print(f"Grade for 65: {calculate_grade(65)}")  # Expected output: D
    print(f"Grade for 50: {calculate_grade(50)}")  # Expected output: F
    print(f"Invalid input (abc): {calculate_grade('abc')}")  # Expected output: Invalid grade input

    # Test calculate_amortization function with sample loan data
    print("\nTesting calculate_amortization function:")
    loan_amount = 100000  # $100,000 loan
    term_years = 30  # 30 years
    interest_rate = 5.0  # 5% annual interest rate

    monthly_payment = calculate_amortization(loan_amount, term_years, interest_rate)
    print(f"Monthly payment for a $100,000 loan over 30 years at 5% interest: {monthly_payment:.2f}")  # Expected output: Monthly payment
