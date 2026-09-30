# [M] MKT-3 | discountModel Updated Before Liabilities Accrue

## Summary
Severity: Medium
Contest weight: 0.0827
Dataset id: 19564
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the setInterestRateModel function, the pending interest is updated with the accrueLiabilities function to correctly account for the outstanding interest having accrued under the previous interest rate model. However in the setDiscountModel function the new _discountModel is set before the interest is updated with the accrueLiabilities function, therefore any pending interest is treated as if it had accrued with the new discount model configured while this is not the case.

## Recommendation
Update the pending interest values with the accrueLiabilities function before updating the _discountModel in the setDiscountModel function.
