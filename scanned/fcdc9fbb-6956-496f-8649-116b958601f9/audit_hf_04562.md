# [H] H-08 | removeLeverage Inaccurate Share Calculation

## Summary
Severity: High
Contest weight: 0.1769
Dataset id: 22165
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When removing leverage, the amount of shares to repay to the Fraxlend vault is calculated based off the amount of the borrowed assets that are desired to be repaid. This is accomplished by calling toShares(). However, this calculation is done before any call is made to the Fraxlend vault. Because of this, the calculation of shares to be repaid does not account for any interest that has been accrued. If enough time has passed or the interest rate is high enough, it will lead to an inaccurate amount of shares to pay off based on the amount of assets provided. This will lead to a revert in repayAssets(), due to insufficient balance and DoS removeLeverage()

## Recommendation
Prior to the calculation of _borrowSharesToRepay in removeLeverage(), call addInterest() on the vault.
