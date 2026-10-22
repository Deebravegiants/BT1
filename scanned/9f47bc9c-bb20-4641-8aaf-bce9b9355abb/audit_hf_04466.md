# [M] M-08 | Liquidations Don't Account For longTokens

## Summary
Severity: Medium
Contest weight: 0.0671
Dataset id: 21962
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
It is possible for a liquidation to send a long token from GMX. For instance, a liquidation can occur when the position was in profit, but fees caused a liquidation. Alternatively, if GMX failed to swap into the collateral token, you can receive the long token. If this were to occur, the token would be stuck within GmxUtils.sol, and unrescuable.

## Recommendation
Check if the long token was sent with a liquidation, and if so transfer it to PerpVault.sol. Additionally, consider adding an admin privileged function to rescue unexpected token transfers.
