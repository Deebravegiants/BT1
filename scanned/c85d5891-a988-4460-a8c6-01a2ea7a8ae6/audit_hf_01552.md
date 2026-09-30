# [M] YieldManager hardcodes slippage to

## Summary
Severity: Medium
Contest weight: 0.0845
Dataset id: 8286
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The current implementation of YieldManager functions moveAssetToYieldManager(), moveAssetToLiquidVault(), and depositYieldIntoLiquidVault() hardcodes the slippage control to 0. This means there is no parameter for slippage control, making all function executions susceptible to significant losses. By setting slippage to 0, these functions accept any amount the relayer returns for swaps or deposits, which can lead to unfavorable outcomes.
The same issue exists in the YieldStrategy.depositToPendle() function.

## Recommendation
Introduce an amountOutMinimum parameter for all affected functions to ensure slippage control.
