# [M] M-17 | Interest Not Accrued Before Rate Update

## Summary
Severity: Medium
Contest weight: 0.1090
Dataset id: 2580
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The acceptRateModelUpdate function allows the pool owner to change the pool's rate model to the pending one after the timelock duration (one day). This rate model is used in the simulateAccrue function to calculate the interest accrued in the pool for the duration since it was last called (pool.lastUpdated) until the current block.timestamp. The issue is that since the acceptRateModelUpdate function doesn’t call accrue first, the next time a function that calls accrue is executed, the calculated interest will be based on the new rate model using the duration since the pool.lastUpdated, which could be a long time before the rate model was updated.

## Recommendation
The acceptRateModelUpdate function should call accrue before updating the rate model to ensure that the interest calculation accurately reflects the old rate model up to the point of the update.
