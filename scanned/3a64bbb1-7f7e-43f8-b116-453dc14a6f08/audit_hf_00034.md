# [M] RSKE-4 | Contract can be initialized many times

## Summary
Severity: Medium
Contest weight: 0.0558
Dataset id: 110
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the IVXRiskEngine contract the initialize function lacks an initializer modifier or any other means to limit the initialization to a single instance. Therefore the owner may initialize the contract multiple times and change key addresses that otherwise should not change after the IVXRiskEngine is in use.

## Recommendation
Add validation that the initialize function in the IVXRiskEngine cannot be called multiple times.
