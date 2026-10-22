# [M] M-03 | Lost Borrow Fee

## Summary
Severity: Medium
Contest weight: 0.0590
Dataset id: 2172
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When users borrow via K33, a part of the borrowed assets is paid as a fee to the feeAddress, which is an arbitrary passed parameter, but is validated to be a whitelisted address. However, whitelisted addresses are also the swap routers and the lending pools. This means users may choose to pay the fee to any other whitelisted address resulting in loss of funds for K33.

## Recommendation
Create a separate validation for the feeAddress.
