# [M] M-19 | Improper Deadline For Fraxlend Swaps

## Summary
Severity: Medium
Contest weight: 0.0484
Dataset id: 22189
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Similarly to M-01, FraxlendPairCore::repayAssetWithCollateral() & FraxlendPairCore::leveragedPosition() does not allow a user to set the block.timestamp for their swap. This exposes users to MEV sandwich attacks, and can cause them to lose out on funds that would have been used to repay their debt.

## Recommendation
Allow users to input the deadline for the swaps.
