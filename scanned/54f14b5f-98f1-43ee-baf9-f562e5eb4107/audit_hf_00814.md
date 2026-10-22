# [H] H-07 | DoS In _removePool By Force Feeding

## Summary
Severity: High
Contest weight: 0.1001
Dataset id: 2550
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
• The _removePool function reverts if the SuperPool still owns assets in the given pool.
• Anyone can deposit into a BasePool and set any SuperPool as the receiver of the assets.
This enables a malicious actor the possibility to front run a _removePool call and deposit one wei of assets into the SuperPool to DoS the call.

## Recommendation
Implement a function that reallocates and removes the pool in one transaction.
