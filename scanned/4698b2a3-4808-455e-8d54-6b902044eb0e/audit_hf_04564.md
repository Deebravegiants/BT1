# [C] C-04 | removeLeverage DoS Due To Inconsistent Amounts

## Summary
Severity: Critical
Contest weight: 0.2194
Dataset id: 22167
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When removing leverage, the user provides the _borrowAssetAmt to be flash loaned. This amount is then used to calculate _borrowSharesToRepay, with the calculation performed by rounding up. Additionally, the LeverageManager grants approval to the Fraxlend pair for exactly the _borrowAssetAmt. Then, on the Fraxlend side, amount to repay is recalculated using this _borrowSharesToRepay. However, this calculation also rounds up. _amountToRepay = _totalBorrow.toAmount(_shares, true);. Because of rounding up twice during this transaction flow, the _amountToRepay ends up being higher than the flash-loaned _borrowAssetAmt. When the internal _repayAsset function attempts to transfer _amountToRepay from LeverageManager to Fraxlend pair, it fails because the LeverageManager neither holds that amount of the borrow asset nor has given that amount of approval to the Fraxlend pair.

## Recommendation
Consider passing in the shares in removeLeverage and calculate the flash loan amount from the shares to mimic FraxLend logic.
