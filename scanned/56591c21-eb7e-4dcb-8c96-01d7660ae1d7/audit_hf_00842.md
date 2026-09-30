# [M] M-15 | setRegistry Should Invoke updateFromRegistry

## Summary
Severity: Medium
Contest weight: 0.0949
Dataset id: 2578
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Pool and PositionManager contracts utilize the Registry contract to retrieve crucial module addresses, and both contracts feature an updateFromRegistry function to update these addresses. In addition, both contracts are equipped with a setRegistry function that enables the owner to modify the Registry contract address. It is advisable to invoke the updateFromRegistry function when setting a new Registry address in order to avoid potential mismatches. Failing to do so may result in the utilization of outdated module addresses until the updateFromRegistry function is manually called.

## Recommendation
Always call the updateFromRegistry function when implementing a new Registry address.
