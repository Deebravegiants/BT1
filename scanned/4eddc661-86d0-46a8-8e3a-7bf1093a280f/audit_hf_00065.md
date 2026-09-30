# [M] M-04 | pendingBalanceVault Underflow

## Summary
Severity: Medium
Contest weight: 0.0775
Dataset id: 141
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The pendingBalanceVault is deducted by the anticipated withdrawal amount when a withdrawal action is initiated. However due to extreme price action in some edge cases the actual balance of the vault may fall below the pending balance, in which case this would cause an underflow revert in all areas where the pending vault balance is added to the vault balance. This would effectively block the queue and shut down the protocol.

## Recommendation
It may not be deemed too complex to handle this edge case in all locations for this iteration of the protocol. However be aware of this edge case and consider handling it.
