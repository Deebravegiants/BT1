# [H] H-10 | Impossible To Repay All Debt In Some Cases

## Summary
Severity: High
Contest weight: 0.2571
Dataset id: 2525
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Users can pay their Position’s whole debt by passing type(uint256).max value as the repayment amount. In that case, PositionManager contract will calculate Position’s total debt and make a call to the underlying pool for the payment.
However, the getBorrowsOf function uses convertToAssets, which rounds down by default, and this causes amount to be paid to round down. This amount is later used in the repay function.
repay in the Pool contract also rounds down the borrowShares amount to burn, which is done to ensure excess debt isn't pushed to other users.
As a result of rounding down twice during the repay flow, the Position will always have 1 borrowShare left even though the user tries to pay whole amount unless the amount is exactly the multiple of asset:share ratio.
This would cause repayment to fail due to MIN_DEBT requirement. Also, even if the Position has other debts that cover MIN_DEBT, the repaid debt pool can not be removed from debtPools array from the Position contract due to remaining 1 share.

## Recommendation
Firstly, getBorrowsOf function should round up. Then, ensure that all borrowShares are burned when all debt is paid.
