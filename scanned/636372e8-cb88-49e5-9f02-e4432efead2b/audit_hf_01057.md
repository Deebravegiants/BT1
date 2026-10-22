# [H] MJR-8 Budget payment blocking

## Summary
Severity: High
Contest weight: 0.0245
Dataset id: 4042
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In pay function of Budget.sol contract defined at Budget.sol#L109 contract sends ETH to recipients in loop using transfer method. As we know transfer method limited by 2300 gas, so any single recipient with payable fallback method can block whole pay function execution

## Recommendation
We recommend to rework payment scheme to claimable model.
