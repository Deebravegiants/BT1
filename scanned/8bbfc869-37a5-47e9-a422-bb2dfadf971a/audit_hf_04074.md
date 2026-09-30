# [H] RH-2 | Wrong Withdrawal Fee Calculation Parameters Passed

## Summary
Severity: High
Contest weight: 0.2328
Dataset id: 20527
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The protocol charges users fees on deposit and withdrawal. Those fees are based on the percentages set by the protocol and on the size in the asset vault's native token of the amount being deposited/withdrawn.

The issue here is due to a share size being passed to the aggregateVault.previewWithdrawalFee function even though the function that calculates the said fee - VaultFees.getWithdrawalFee() assumes it is a native token amount.

As the vault's TVL grows and more yield is gained through its strategies, each share will be worth more. However, this will not be represented when calculating the withdrawal fee as the calculations will think that the amount of shares passed in is the native token amount.

This directly impacts the protocol as the fees it will receive on withdrawal will be substantially lower than expected leading to a loss of fees for the protocol.

## Recommendation
To mitigate the issue convert the vault shares into their native asset’s worth before passing them to aggregateVault.previewWithdrawalFee().
