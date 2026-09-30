# [M] M-09 | Execution Fee Required For Swaps

## Summary
Severity: Medium
Contest weight: 0.0705
Dataset id: 21963
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the deposit and withdraw functions the _payExecutionFee function is called regardless of if the action will require a GMX order. For example, if the vault is 1x long and a paraswap swap will be used to execute the swap, the execution fee for a GMX swap is still collected. This unnecessarily charges the user for an action that will not occur and offers them no refund in the event that a normal swap is used.

## Recommendation
Consider refunding the executionFee to the user if a GMX action is not performed on a swap.
