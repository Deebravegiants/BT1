# [M] M-02 | Interest Lost On Low Decimal Tokens

## Summary
Severity: Medium
Contest weight: 0.0952
Dataset id: 2157
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the accrueInterest function, the interest calculation interestFactor.mul(_totalBorrows).div(1e18) can round down to zero for low-decimal tokens (such as USDC), particularly when the borrow rate or total borrows are low. Specifically, when the product of interestFactor and _totalBorrows is less than 1e18, the division results in zero. This leads to a loss of interest for lenders, as the interestAccumulated is zero. Furthermore, this can cause a discrepancy between totalBorrows and accountBorrows, since accountBorrows does not experience the same precision loss.

## Recommendation
Use a higher precision for the rate values to accommodate tokens with fewer decimals, ensuring that the computed interest does not round to zero.
