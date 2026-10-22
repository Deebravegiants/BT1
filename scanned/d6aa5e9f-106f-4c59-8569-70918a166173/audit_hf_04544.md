# [M] M-04 | Margin Liquidations Should Remove Pending Order

## Summary
Severity: Medium
Contest weight: 0.0691
Dataset id: 22109
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
During liquidateMarginOnly, the liquidated account may have a pending order which is not removed.
The order cannot be settled and if market price were to go outside of the priceLimit range, the order
can now be cancelled.
However, as the account has been liquidated, the cancel order settlement reward is charged as debt
to the account but may never be repaid. This debt will exist in the system as permanent bad debt.

## Recommendation
Remove any pending order during margin liquidations.
