# [M] Swaps should use the deadline argument on top of minimumAmountOut

## Summary
Severity: Medium
Contest weight: 0.0550
Dataset id: 16152
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Swapping with block.timestamp as deadline means validators may do MEV up to the minimumAmountOut.
https://github.com/TrestleProtocol/Audit-Contracts/blob/main/src/Trestle.sol#L441
https://github.com/TrestleProtocol/Audit-Contracts/blob/main/src/Trestle.sol#L709
https://github.com/TrestleProtocol/Audit-Contracts/blob/main/src/Trestle.sol#L727

## Recommendation
Recommendation not found
