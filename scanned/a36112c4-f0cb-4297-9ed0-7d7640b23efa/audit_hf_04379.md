# [M] M-07 | Incorrect Calculation Of USDC Required Per Batch

## Summary
Severity: Medium
Contest weight: 0.0821
Dataset id: 21587
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Revenue contract tracks the amount of USDC tokens required per batch id, for users to redeem.
It uses the fixedValorToUsdcRateScaled to calculate the USDC amount based on the batch valor amount.
This USDC amount calculation is missing the VALOR_TO_USDC_RATE_PRECISION correction, so the value returned is greater than expect, thus invalid. Additionally, if the batch id is not claimable yet, the fixedValorToUsdcRateScaled value is not set (value 0), so all amounts will be 0 due to the multiplication.

## Recommendation
Add a division by VALOR_TO_USDC_RATE_PRECISION to fix the units.
