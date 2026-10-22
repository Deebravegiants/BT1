# [H] H-14 | Withdrawers Lose Funds Due To Collateral Check

## Summary
Severity: High
Contest weight: 0.1663
Dataset id: 21973
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In GMX if a decrease order is deemed to leave the remaining position with insufficient collateral for its open interest, then the initialCollateralDelta is reassigned to 0. This will result in withdrawals which are deemed to leave behind insufficient collateral via the willPositionCollateralBeSufficient check in receiving no collateral tokens out from GMX. Therefore, withdrawers which are affected by this case lose all collateral and will only receive a portion of any profit which was gained from the position.

## Recommendation
Validate that the willPositionCollateralBeSufficient check in GMX will not be triggered upon creating withdrawals from GMX, and if it is triggered upon execution of a decrease order for a withdrawal, adjust the user’s shares such that they can claim their portion of the collateral that did not come out of the decrease order.
