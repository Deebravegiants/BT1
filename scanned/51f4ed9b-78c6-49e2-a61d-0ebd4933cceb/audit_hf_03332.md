# [M] GSU-2 | Gas Price Deficit

## Summary
Severity: Medium
Contest weight: 0.0688
Dataset id: 18183
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the validateExecutionFee function, the current tx.gasprice is used to estimate the gas price in the block of the execution. However the current tx.gasprice can be significantly different from the tx.gasprice actually experienced in the block of execution. This allows the keeper to expend more gas than the executionFee in the case where the tx.gasprice is greater in the block of execution.

## Recommendation
Be wary of the potential gasprice difference and set the ESTIMATED_GAS_FEE_MULTIPLIER_FACTOR accordingly.
