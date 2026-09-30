# [C] C-1 Epoch Manipulation

## Summary
Severity: Critical
Contest weight: 0.1865
Dataset id: 7377
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
This issue has been identified in the deposit function of the Prestaking contract.
The epochIndex is not properly set or stored within the staking wallet structure. As a result, users can
manipulate the staking mechanism by selecting any epoch during deposit, allowing them to exploit epochs
with more favorable conditions, such as earlier unlock times. This can lead to users bypassing the intended
locking periods and gaining access to their staked tokens earlier than allowed, breaking the fairness of the
staking system.
The issue is classified as Critical severity because it allows users to bypass staking conditions, potentially
undermining the entire staking system.

## Recommendation
We recommend setting and storing the epochIndex in the StakingWallet structure to ensure that the
staking conditions, including the lockup and release times, are tied to the correct epoch.
