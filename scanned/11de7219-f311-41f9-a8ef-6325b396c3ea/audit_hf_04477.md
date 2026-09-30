# [M] M-02 | Missing Feature Execution Validation

## Summary
Severity: Medium
Contest weight: 0.0893
Dataset id: 21975
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Orders can become stuck halting protocol functionality when order execution is disabled. When an order is created GMX will check that the create order feature is enabled. If it is not, it will revert. However, during order creation there is no check that the order execution feature will be disabled. This means that when order execution is disabled Gamma orders will still successfully be created but will not execute due to the feature validation in _executeOrder until the feature is enabled again. Halting protocol functionality for a period of time.

## Recommendation
Before sending an order to GMX check that the execution feature is enabled.
