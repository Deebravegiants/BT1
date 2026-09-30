# [M] MKTU-8 | Precision Loss For Funding Fees

## Summary
Severity: Medium
Contest weight: 0.0491
Dataset id: 18191
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When computing the cache.fundingUsd, a USD amount with 30 decimals of precision is divided by 1e30: cache.sizeOfLargerSide / Precision.FLOAT_PRECISION. This results in precision loss on the order of magnitude of tens of cents for the distribution of funding fees.

## Recommendation
Consider if this magnitude of precision loss is acceptable and adjust the calculation if it isn’t.
