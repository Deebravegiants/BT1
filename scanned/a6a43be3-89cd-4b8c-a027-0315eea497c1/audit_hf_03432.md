# [M] DPCU-2 | Fees May Be Errantly Credited To The Pool

## Summary
Severity: Medium
Contest weight: 0.0998
Dataset id: 18739
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the processForceClose function, the amountForPool is the remainingCollateral minus the fundingFees. However it is possible in some cases that this amountForPool includes amounts that were meant to be subtracted from the collateral for other beneficiaries other than the pool. For example the feeReceiver, uiFeeReceiver, and affiliate. This situation can arise when the pendingCollateralDeduction is only slightly larger than the remaining collateral, and the exact deduction that put the collateral deduction over the remaining collateral threshold is one of these fees that should not be distributed to the pool.

## Recommendation
Consider decrementing these fees from the amountForPool and crediting as much as possible to the rightful receivers.
