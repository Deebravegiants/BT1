# [M] NativeVault.finishWithdrawal() doesnt reset withdrawalMap[withdrawalKey] after executing the withdrawal

## Summary
Severity: Medium
Contest weight: 0.3846
Dataset id: 13990
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In NativeVault.finishWithdrawal(), the withdrawal to execute is fetched with withdrawalMap[withdrawalKey]:
```solidity
NativeVaultLib.Storage storage self = _state();
NativeVaultLib.QueuedWithdrawal memory startedWithdrawal = self.withdrawalMap[withdrawalKey];
```
However, after the pending withdrawal is executed, self.withdrawalMap[withdrawalKey] isn't reset in storage. This allows a user to call finishWithdrawal() repeatedly with the same withdrawalKey to withdraw all his assets, effectively bypassing MIN_WITHDRAWAL_DELAY.

## Recommendation
Consider clearing withdrawalMap[withdrawalKey] as such:
```diff
NativeVaultLib.Storage storage self = _state();
NativeVaultLib.QueuedWithdrawal memory startedWithdrawal = self.withdrawalMap[withdrawalKey];
+ delete self.withdrawalMap[withdrawalKey];
```
