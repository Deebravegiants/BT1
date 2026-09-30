# [M] DPCU-3 | swapProfitToCollateralToken Invalid Impact

## Summary
Severity: Medium
Contest weight: 0.0885
Dataset id: 18184
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When the swapProfitToCollateralToken swap is performed, the pnlAmountForPool has not yet been decremented from the poolAmount. Therefore the price impact calculation as well as subsequent validation checks during swapProfitToCollateralToken are based on the pnlAmountForPool not being withdrawn from the poolAmount, but yet still being swapped. This leads to inaccurate price impact being applied during the swap as well as validation that is hinged upon a temporary invalid state of the pool accounting.

## Recommendation
In the case where the swapProfitToCollateralToken swap is performed, account for the user’s profit tokens first being removed from the pool before they are used to swap in the pool.
