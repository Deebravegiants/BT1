# [M] CAUL-1 | Errant maxRate Validation

## Summary
Severity: Medium
Contest weight: 0.0528
Dataset id: 132
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the cook function the ACTION_UPDATE_EXCHANGE_RATE action includes a minRate and maxRate to bound the allowed updated rate. The rate is validated to be > minRate as well as > maxRate if a maxRate is set. However this misconstrues the meaning of a maxRate as the rate should be validated to be < maxRate.

## Recommendation
Validate that the rate is < maxRate when the maxRate ≠ 0.
