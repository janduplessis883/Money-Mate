import pytest
import pandas as pd
from pandas.testing import assert_frame_equal
from datetime import datetime

# Assume classify_by_type and refine_by_name functions are defined elsewhere and imported here
from money_mate.classification import classify_by_type, refine_by_name, prep_account_statement, calculate_smoking_adjustment, apply_smoking_adjustment, smoke_max_value, smoke_min_value

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

def test_prep_account_statement():
    # Sample data
    data = {
        "Transaction ID": [1, 2],
        "Category split": ["split1", "split2"],
        "Receipt": ["receipt1", "receipt2"],
        "Date": ["01/01/2023", "02/01/2023"],
        "Type": ["Shopping", "Groceries"],
        "Name": ["Amazon", "J M S Foods"],
        "Amount": [-12, -14],
    }

    df = pd.DataFrame(data)

    # Expected output
    expected_data = {
        "Date": [datetime(2023, 1, 1), datetime(2023, 1, 2)],
        "Type": ["Shopping", "Groceries"],
        "Name": ["Amazon", "J M S Foods"],
        "Amount": [-12, -14],
        "year": [2023, 2023],
        "month": [1, 1],
        "month_name": ["Jan", "Jan"],
        "custom_category": ["Shopping", "Smoking"],
        "Cumulative Amount": [-12, -26],
    }

    expected_df = pd.DataFrame(expected_data)

    # Apply the function
    result_df = prep_account_statement(df)

    print(result_df)

    # Check if the result matches the expected DataFrame
    assert_frame_equal(result_df, expected_df)

if __name__ == "__main__":
    pytest.main()
