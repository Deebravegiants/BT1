# [M] Insufficient input validation

## Summary
Severity: Medium
Contest weight: 0.0902
Dataset id: 2922
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The DKIMRecoverySigValidator contract uses the AccInfo struct that has fields which values are not validated. Here are the fields that are problematic:
- secondaryKey can be the zero address, which can result in a loss of access to the AmbireAccount wallet
- waitUntilAcceptAdded is a time value and can be too big, resulting in inability to add DKIM keys
- waitUntilAcceptRemoved is a time value and can be too big, resulting in inability to remove DKIM keys
- onlyOneSigTimelock is a time value and can be too big, resulting in forever locked recovery

## Recommendation
Add sensible upper boundaries for the time values and a check that secondaryKey != address(0).
