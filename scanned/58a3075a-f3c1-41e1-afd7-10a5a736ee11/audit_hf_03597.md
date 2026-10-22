# [H] GLOBAL-1 | Snapshot System Prone To Instant Balance Change

## Summary
Severity: High
Contest weight: 0.1871
Dataset id: 19576
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The snapshot system was implemented in Ambit V2 to prevent the manipulation of the utilization rate through instantaneous balance changes in the Depositor Vault. However, the system only examines the latest snapshot, which can be trivially updated because the function takeSnapshot is public. A user can take a snapshot right after depositing in the vault, and now the snapshot will reflect the current balance. Consequently, a user can still instantly manipulate the utilization rate at will through their deposits and withdrawals and take a snapshot right after.

## Recommendation
Modify the visibility of function of takeSnapshot to private. Furthermore, take a snapshot upon borrowing and repaying as the total liabilities are modified. Consider taking a weighted average of the assets available across the past 4-10 snapshots so it is less prone to instantaneous manipulation. Also, consider utilizing a minimum deposit and borrow amount as well to limit a user from trivially creating many snapshots and pushing the 4-10 snapshots back.
