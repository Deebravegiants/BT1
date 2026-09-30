# [C] C-03 | Redeeming USDC Revenue Functionality Broken

## Summary
Severity: Critical
Contest weight: 0.1450
Dataset id: 21586
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In order to claim USDC revenue from ledger, the owner should mark the batch as claimed using batchPreparedToClaim. This will also reduce the totalValorAmount as much as the redeemed amount in the batch. The issue is that totalValorAmount is always zero, causing fixedValorToUsdcRateScaled to be zero as well. Consequently, attempts to call batchPreparedToClaim fail with the BatchValorToUsdcRateIsNotFixed error, making it impossible to mark the batch as claimed and preventing users from executing USDC claims.

## Recommendation
Increase totalValorAmount by pendingValor when _updateValorVarsAndCollectUserValor is called.
