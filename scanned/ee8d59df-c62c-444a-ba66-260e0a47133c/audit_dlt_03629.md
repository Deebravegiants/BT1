# [H] [ADRIRO-NEW-H-01] VotiumStrategy withdrawal can still be executed with minimal delay

## Summary
Severity: High
Chain: Smart contract
Component: 2023-10-asymmetry-mitigation
Published: 2023-10-25
Source: https://github.com/code-423n4/2023-10-asymmetry-mitigation-findings/issues/45
Type: code-finding

## Details
# Lines of code

https://github.com/asymmetryfinance/afeth/blob/74f340568480aa03d043e970fcf2578bea037cf6/contracts/AfEth.sol#L206


# Vulnerability details

## Summary

Within the mitigation changes, the sponsor has introduced a minimum delay of one epoch for VotiumStrategy withdrawals, in order to mitigate different issues related to the exposure to CVX . The fix contains an edge case which could still be used to make deposits in AfEth with minimal exposure to CVX.

## Impact

Epochs in Convex are synchronized with Curve gauge epochs, which are weekly periods that start each Thursday at 00:00 UTC.

For example, at the time of writing the current epoch is 85. This epoch started at timestamp `1698278400`, which is Thursday Oct 18th at 00:00 UTC. The next epoch, 86, starts on Thursday Oct 25th at 00:00 UTC, which also marks the end of epoch 85.

One of the new changes in the updated code is the introduction of a minimum delay of one epoch in VotiumStrategy withdrawals. Even if the available CVX balance (CVX held by the contract plus any unlockable balance in Convex) is enough to cover the withdrawal, the request is delayed until the next epoch. Locked balances are still implemented as they were before, because any locked balance naturally implies waiting for at least the next epoch.

The updated code can be seen in the `requestWithdraw()` function:

https://github.com/asymmetryfinance/afeth/blob/74f340568480aa03d043e970fcf2578bea037cf6/contracts/strategies/votium/VotiumStrategy.sol#L78-L96

```solidity
78:         uint256 cvxAmount = (_amount * _priceInCvx) / 1e18;
79:         cvxUnlockObligations += cvxAmount;
80: 
81:         uint256 totalLockedBalancePlusUnlockable = unlockable +
82:             trackedCvxBalance;
83: 
84:         if (totalLockedBalancePlusUnlockable >= cvxUnlockObligations) {
85:             withdrawIdToWithdrawRequestInfo[
86:                 latestWithdrawId
87:             ] = WithdrawRequestInfo({
88:                 cvxOwed: cvxAmount,
89:                 withdrawn: false,
90:                 epoch: currentEpoch + 1,
91:                 owner: msg.sender
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-10-asymmetry-mitigation-findings/issues/45_
