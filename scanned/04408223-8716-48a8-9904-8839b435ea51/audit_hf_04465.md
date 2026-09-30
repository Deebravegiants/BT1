# [M] M-07 | Gas Estimation Uses Old Key

## Summary
Severity: Medium
Contest weight: 0.0483
Dataset id: 21961
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the getExecutionGasLimit function the ESTIMATED_GAS_FEE_BASE_AMOUNT key is used to estimate the gas. However with the upgrade of GMX V2.1 the ESTIMATED_GAS_FEE_BASE_AMOUNT_V2_1 key is now used to validate the executionFee base amount upon creating an order.

## Recommendation
Use the updated ESTIMATED_GAS_FEE_BASE_AMOUNT_V2_1 key in the getExecutionGasLimit function.
