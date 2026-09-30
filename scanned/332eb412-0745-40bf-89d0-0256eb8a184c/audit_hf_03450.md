# [M] GSU-1 | Decrease Swap Type Not Included In Gas Estimation

## Summary
Severity: Medium
Contest weight: 0.0912
Dataset id: 18860
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a decrease order contains a decreasePositionSwapType other than NoSwap it will execute an additional swap in the current market. However this additional swap is not accounted for in the estimateExecuteDecreaseOrderGasLimit gas estimation. Therefore these orders will consume gas for an extra swap that is not accounted for in the estimated gas cost. Additionally if this extra swap were to be accounted for by default in the base decreaseOrderGasLimit, it would be requiring users with a NoSwap to put down more initial executionFee than necessary.

## Recommendation
Account for an additional gasPerSwap for decrease orders that have a decreasePositionSwapType other than NoSwap.
