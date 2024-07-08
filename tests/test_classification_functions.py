import pytest
import pandas as pd
from pandas.testing import assert_frame_equal
from datetime import datetime

# Assume classify_by_type and refine_by_name functions are defined elsewhere and imported here
from money_mate.classification import classify_by_type, refine_by_name, prep_account_statement, calculate_smoking_adjustment, apply_smoking_adjustment, smoke_max_value, smoke_min_value, calculate_variable_expenses

def test_calculate_smoking_adjustment():
    # Sample data
    data = {
        "custom_category": ["Groceries", "Groceries", "Groceries", "Smoking"],
        "Amount": [-22, -14, -9, -13]
    }

    df = pd.DataFrame(data)

    # Expected adjustment amount
    expected_adjustment_amount = -14  # Sum of -12 and -14 (within -11 and -15 range)

    # Apply the function
    result_adjustment_amount = calculate_smoking_adjustment(df)

    # Check if the result matches the expected adjustment amount
    assert result_adjustment_amount == expected_adjustment_amount



def test_apply_smoking_adjustment():
    # Sample data
    data = {
        "custom_category": ["Groceries", "Groceries", "Groceries", "Smoking"],
        "Amount": [-12, -14, -9, -13]
    }

    df = pd.DataFrame(data)

    # Expected output
    expected_data = {
        "custom_category": ["Smoking", "Smoking", "Groceries", "Smoking"],
        "Amount": [-12, -14, -9, -13]
    }

    expected_df = pd.DataFrame(expected_data)

    # Apply the function
    result_df = apply_smoking_adjustment(df)

    # Check if the result matches the expected DataFrame
    assert_frame_equal(result_df, expected_df)



def test_calculate_variable_expenses():
    # Sample data
    data = {
        "custom_category": ["Barber", "Eating Out", "Groceries", "Holiday", "Shopping", "Smoking", "Transport", "Other", "Income", "Rent"],
        "Budget": [50, 100, 150, 200, 250, 300, 350, 400, 500, 600]
    }

    df = pd.DataFrame(data)

    # Expected result
    expected_variable_expenses = sum([50, 100, 150, 200, 250, 300, 350, 400])

    # Apply the function
    result_variable_expenses = calculate_variable_expenses(df)

    # Check if the result matches the expected value
    assert result_variable_expenses == round(expected_variable_expenses, 2)

if __name__ == "__main__":
    pytest.main()
