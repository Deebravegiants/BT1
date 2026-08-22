# [M] [ADRIRO-NEW-M-02] AfEth withdrawals are delayed even if the vAfEth withdrawal amount is zero

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-10-asymmetry-mitigation
Published: 2023-10-25
Source: https://github.com/code-423n4/2023-10-asymmetry-mitigation-findings/issues/52
Type: code-finding

## Details
# Lines of code

https://github.com/asymmetryfinance/afeth/blob/74f340568480aa03d043e970fcf2578bea037cf6/contracts/AfEth.sol#L206


# Vulnerability details

## Summary

While zero amount withdrawals of SafEth have been prevented, the updated codebase still executes the withdrawal process for zero amount withdrawals of vAfEth, creating an unnecessary delay in AfEth withdrawals.

## Impact

In AfEth, the withdrawal process is initiated by requesting a withdrawal using `requestWithdraw()`. As we can see in the implementation, even if the resulting amount of vAfEth (`votiumWithdrawAmount`) is zero, the function still calls `VotiumStrategy::requestWithdraw()`:

https://github.com/asymmetryfinance/afeth/blob/74f340568480aa03d043e970fcf2578bea037cf6/contracts/AfEth.sol#L214-L219

```solidity
214:         uint256 votiumWithdrawAmount = (withdrawRatio *
215:             trackedvStrategyBalance) / 1e18;
216:         uint256 withdrawTimeBefore = withdrawTime(votiumWithdrawAmount);
217:         uint256 vEthWithdrawId = AbstractStrategy(vEthAddress).requestWithdraw(
218:             votiumWithdrawAmount
219:         );
```

Drilling down into `VotiumStrategy::requestWithdraw()`, we can that even for a zero amount the request must undergo a delay:

https://github.com/asymmetryfinance/afeth/blob/74f340568480aa03d043e970fcf2578bea037cf6/contracts/strategies/votium/VotiumStrategy.sol#L78-L96

```solidity
78:         uint256 cvxAmount = (_amount * _priceInCvx) / 1e18;
79:         cvxUnlockObligations += cvxAmount;
80: 
81:         uint256 totalLockedBalancePlusUnlockable = unlockable +
82:             trackedCvxBalance;
83: 
84:         if (totalLockedBalancePlusUnlockable >= cvxUnlockObligations) {
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-10-asymmetry-mitigation-findings/issues/52_
