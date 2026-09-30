# [M] Debt is not updated when removing margin

## Summary
Severity: Medium
Contest weight: 0.1497
Dataset id: 20190
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Debt is not updated when removing margin from a position. Traders are allowed to remove margin/collateral from their positions: vy#L528-L546. As you can see, the position can only have collateral removed if it is not liquidable: vy#L487. The problem is that the total_debt_shares[_debt_token] is not updated when checking whether the position is liquidable nor when calling remove_margin. You can see on the following links the progression of the function calls to calculate whether a position is liquidable or not: vy#L444 vy#L1142 vy#L1099 vy#L1111 vy#L1117C16-L1117C16. As seen, total_debt_shares[_debt_token] is not updated to the current total_debt_shares[_debt_token] by calling _update_debt and therefore a stale total_debt_shares[_debt_token] is used to calculate whether a position is liquidable. Allowing positions that are in fact liquidable remove margin because the debt is not updated. Not updating the debt before removing collateral (margin) from your position does allow a trader to remove collateral from a liquidable position.

## Recommendation
Call _update_debt at the beginning of the remove margin function.
