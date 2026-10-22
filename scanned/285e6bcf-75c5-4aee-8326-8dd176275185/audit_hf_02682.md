# [H] Malicious Node Operators Can Cause a DoS through DistributeRewards() And SettleFunds(), Locking User Funds

## Summary
Severity: High
Contest weight: 0.5781
Dataset id: 14539
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
During the onboarding process, node operators - irrespective of whether they are permissioned or permissionless - can define their unique operatorRewardAddress when invoking the onboardNodeOperator() function. Presently, the system only checks to ensure that the reward address does not equal to the zero address.
This current system, however, leaves room for abuse. A malicious node operator can, during onboarding, deliberately set their operatorRewardAddress to a contract address. When the distributeRewards() or settleFunds() functions are triggered, the contract can cause a reversion at line [75] and line [100] respectively in ValidatorWithdrawalVault:
```solidity
sendValue(getNodeRecipient(), operatorShare);
```
Moreover, node operators have can alter their operatorRewardAddress at will through the updateOperatorDetails() function. This allows malicious operators to manipulate when to trigger a reversion in distributeRewards() and settleFunds() functions.

## Recommendation
The Pull over Push pattern could be used to ensure that user and protocol shares can be distributed even if the operatorRewardAddress is assigned to a malicious contract.
One viable solution could involve maintaining a record of the nodeRefundBalance.
