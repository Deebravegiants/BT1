# [H] Users can modify a cancelled or-

## Summary
Severity: High
Contest weight: 0.2117
Dataset id: 1921
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In Bracket, OracleLess and StopLimit a user can modify a canceled order, allowing them to withdraw the order tokens twice.
In Bracket, OracleLess and StopLimit there is no validation on whether an order has been canceled before allowing modifications. This allows users to cancel an order, withdrawing all of the tokens, and after that modifying it by reducing the amountIn to 1, withdrawing the rest of the tokens for a second time.
Internal pre-conditions
External pre-conditions
Attack Path
1. User creates an order with amountIn set to 1e18.
2. The user cancels the order, withdrawing 1e18 of the tokens.
3. Finally, they modify the order, decreasing amountIn to 1, withdrawing 1e18 - 1 of the already withdrawn tokens.
4. The attack can be performed several times until all of the contract's tokens are drained.
Bracket, OracleLess and StopLimit can be drained.

## Recommendation
Make sure that a canceled order cannot be modified.
