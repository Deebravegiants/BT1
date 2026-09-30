# [C] Multiple unstake() calls at the same position can drain the vault

## Summary
Severity: Critical
Contest weight: 0.1658
Dataset id: 5769
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the unstake() function, when a user unstakes their position, all staked tokens plus accrued interest are sent back to the original staker. At this point, the staker should not be allowed to unstake from the same position again. However, there is no restriction in the function preventing multiple unstake calls, which allows users to withdraw the same amount of Gold tokens repeatedly from a single position. A malicious user can exploit this vulnerability to drain the vault by calling unstake() multiple times on the same position.

## Recommendation
To prevent this vulnerability, consider implementing one of these solutions:
• Close the position after the unstake operation is complete.
• Set the position's amount to zero after a successful unstake.
• Add a flag to track whether a position has already been unstaked.
