# [M] M-3 DefaultOperatorFiltererUpgradeable initializer is not called

## Summary
Severity: Medium
Contest weight: 0.0521
Dataset id: 7927
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
FantiumNFTV1 class inherits DefaultOperatorFiltererUpgradeable but it's initializer is not called together
with other base classes initializers in the initialize() method at FantiumNFTV1.sol#L168.
Due to this, the full functionality related to OperatorFilterRegistry becomes unavailable.

## Recommendation
We recommend adding the DefaultOperatorFilterer_init() call to FantiumNFTV1 initializer.
