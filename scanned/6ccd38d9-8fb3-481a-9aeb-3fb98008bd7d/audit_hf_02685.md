# [M] StaderConfig Cannot Be Updated

## Summary
Severity: Medium
Contest weight: 0.0830
Dataset id: 14542
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
StaderConfig serves as a central contract that maintains all protocol settings and access control, crucial for the protocol’s regular operation. Every key contract within the codebase holds the current StaderConfig address as a reference and provides a method for altering the StaderConfig address, namely updateStaderConfig().
However, ETHx.sol and OperatorRewardsCollector.sol contracts lack a function to update the StaderConfig in case of future changes to this address.

## Recommendation
The testing team recommends adding the updateStaderConfig() function, similar to the setter function present in all other key contracts in the ETHx codebase.
