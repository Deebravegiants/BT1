# [M] M-12 | Inaccurate Imbalance Check In _checkImbalanceLimitOpen

## Summary
Severity: Medium
Contest weight: 0.1447
Dataset id: 169
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The function _checkImbalanceLimitOpen inaccurately calculates the imbalance when initiating the opening of a new position because it does not account for the position fees deducted. This miscalculation could allow the system to enter a state where it is unbalanced beyond what should be possible after the action is validated.
This is because _checkImbalanceLimitOpen calculates the imbalanceBps by assuming that the balance of the vault is equal to just s._balanceVault + s._pendingBalanceVault and that the balance of the long side is equal to s._balanceLong + openCollatValue where openCollatValue is equal to params.amount.
However, openCollatValue does not reflect the true position value and should be instead equal to data_.positionValue (params.amount minus the position fee paid). On the other hand, currentVaultExpo should also include the position fee which can be calculated as params.amount - data_.positionValue. Do notice that this update is performed after _checkImbalanceLimitOpen check.

## Recommendation
Consider updating the imbalance check to include the fees.
