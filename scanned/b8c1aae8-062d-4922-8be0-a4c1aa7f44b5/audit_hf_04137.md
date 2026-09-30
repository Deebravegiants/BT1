# [H] EWT-1 | All Attempted Withdrawals Will Fail in EigenLayer M1

## Summary
Severity: High
Contest weight: 0.1511
Dataset id: 20597
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a staker wants to withdraw their eigen shares through function withdrawUsingEigenShares, the function _queueWithdraw is called which queues a withdrawal through the delegation manager: delegationManager.queueWithdrawals(arrayify(withdraw)); However, the currently deployed M1 DelegationManager does not support function queueWithdrawals and all calls to it will revert. Consequently, users are entirely unable to withdraw their restaked assets.

## Recommendation
Consider making the contracts upgradeable such that when EigenLayer upgrades to the M2 contracts, the Rest Vault’s functionality can be updated. Furthermore, add functions for user to withdraw their eigen shares through the current M1 StrategyManager with function queueWithdrawal and completeQueuedWithdrawal.
