# [C] C-01 | Incorrect Amounts Are Used During Withdrawals

## Summary
Severity: Critical
Contest weight: 0.1183
Dataset id: 2511
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When assets are withdrawn from SuperPool, the redeem function in the base pool is invoked. This function requires the share amount as an input. However, during this call, the asset amount is provided instead, leading to significant accounting issues and potential loss of funds.

## Recommendation
To address this issue, it is recommended to convert the user-provided asset amount to the corresponding share amount before proceeding with the redemption process.
