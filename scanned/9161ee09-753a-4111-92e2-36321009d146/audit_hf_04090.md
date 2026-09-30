# [M] VAULT-1 | Vault Owner Can Cancel Liquidation

## Summary
Severity: Medium
Contest weight: 0.1017
Dataset id: 20545
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the cancelWithdrawal function, the vault owner can cancel liquidations which is essentially a
withdrawal of the GM tokens. When a liquidator uses prepareForLiquidation, they trigger a forced
withdrawal from the underwater vault.
The issue arises as the cancelWithdrawal function doesn't distinguish between user-initiated
withdrawals and forced withdrawals (like liquidations). This allows a user to repeatedly cancel
withdrawal attempts, causing a loss of funds for both the protocol (insolvency) and the liquidator as
only the first liquidation execution fee is covered by the user.

## Recommendation
Differentiate between normal withdrawals and those from liquidation. Restrict the vault owner from
calling the cancelWithdrawal function when there is a pending withdrawal initiated by the
prepareForLiquidation function.
