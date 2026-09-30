# [M] M-07 | Old Estimated Execution Base Gas Fee Used

## Summary
Severity: Medium
Contest weight: 0.0901
Dataset id: 21435
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The EXECUTION_GAS_FEE_BASE_AMOUNT key has been replaced with an EXECUTION_GAS_FEE_BASE_AMOUNT_V2_1 key to allow an increased base fee to be charged for additional gas expenditures in V2.1. However the corresponding estimated fee which is required upon order creation is still based upon the ESTIMATED_GAS_FEE_BASE_AMOUNT which corresponds with the old estimated base gas fee amount. As a result the estimated fee which users are required to pay upfront may be insuﬃcient to cover the gas expenditure for order execution in the V2.1 system.

## Recommendation
Consider implementing a ESTIMATED_GAS_FEE_BASE_AMOUNT_V2_1 which corresponds to the EXECUTION_GAS_FEE_BASE_AMOUNT_V2_1 value.
