# [H] Withdrawing funds can lead to wrong accounting

## Summary
Severity: High
Contest weight: 0.3313
Dataset id: 16236
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The users can withdraw their funds from the Vault and if there is not enough LYX in the contract (totalUnstaked), a delayedAmount will be deducted from totalStaked and be assigned to _pendingWithdrawals[beneficiary]: nonReentrant whenNotPaused { uint256 immediateAmount = amount > totalUnstaked ? totalUnstaked : amount; uint256 delayedAmount = amount - immediateAmount; totalUnstaked -= immediateAmount; totalStaked -= delayedAmount; //@audit totalStaked is decreased _pendingWithdrawals[beneficiary] += delayedAmount; This means that when LYX is unstaked and a validator is exited, the user will be able to claim the delayedAmount which is already deducted from the totalStaked. However, the LYX is still staked and the validator is running until it is exited. However, as mentioned above, rewards are constantly sent to the Vault automatically. This can lead to a scenario when the _pendingWithdrawals[beneficiary] is a small amount and it is beneficial for the Vault to wait few days and to accrue rewards instead of exiting a validator. As mentioned in the docs, a withdrawal can take up to 8 days. Let's look at an example: -. A user wants to withdraw 10 LYX but totalUnstaked = 9.5 LYX. /. 0.5 LYX is deducted from totalStaked and _pendingWithdrawals[beneficiary] += 0.5 LYX. 0. Instead of exiting validator, there are enough rewards so the user can claim the delayedAmount which is 0.5. 1. Now, the totalStaked is 0.5 less than it should be because the funds were deducted beforehand. In the long run, this will seriously mess up the whole internal accounting if this happens a lot of times which is quite likely for small amounts.

## Recommendation
Decrease totalStaked only when the LYX is actually unstaked and sent to the Vault.
