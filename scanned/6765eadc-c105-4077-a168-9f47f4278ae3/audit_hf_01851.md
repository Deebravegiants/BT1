# [H] H-2 Proposal duration is not set

## Summary
Severity: High
Contest weight: 0.1187
Dataset id: 10275
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
There is an issue at the lines: daoVetoGrantImplant.sol#L236, daoVetoGrantImplant.sol#L288, and daoVetoGrantImplant.sol#L346. New proposals are created and initialized with the id, start time, and calldata. But the proposal duration is not set, which will lead to the passing check at line daoVetoGrantImplant.sol#L174. All created proposals can be executed instantly without waiting for duration time.

## Recommendation
We recommend setting the proposal duration at the time when it is created.
