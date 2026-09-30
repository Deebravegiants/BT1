# [M] whenNotPaused should not be used while redeem

## Summary
Severity: Medium
Contest weight: 0.0549
Dataset id: 6489
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Pausing functionality is a great feature in times of emergency. But you should be careful about which functionalities you want to pause and which not. The redeem function should be free of any Pausing constraints, otherwise if owner decides to never unpause the contract then user funds will get stuck in the contract.

## Recommendation
Consider removing the whenNotPaused modifier from redeem().
