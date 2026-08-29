# [M] Unsafe cast of `pointsPerShare` can cause wrong reward calculation

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-10-merit-circle
Published: 2022-10-14
Source: https://github.com/sherlock-audit/2022-10-merit-circle-judging/issues/46
Type: sherlock-finding

## Details
berndartmueller

medium

# Unsafe cast of `pointsPerShare` can cause wrong reward calculation

## Summary

The unsafe cast of `pointsPerShare` from `uint256` to `int256` can cause less earned rewards than anticipated.

## Vulnerability Detail

The unsafe cast of `pointsPerShare` to `int256` can cause its value to be different from the correct value. If the unsigned value of `pointsPerShare` is above the maximum signed value `type(int256).max`, it will be interpreted as a negative value instead. Then `pointsCorrection[account]` will be incorrect and the amount of earned rewards for a user will be less than expected.

## Impact

A user will earn fewer rewards than expected.

## Code Snippet

[base/AbstractRewards.sol#L126](https://github.com/sherlock-audit/2022-10-merit-circle/blob/main/merit-liquidity-mining/contracts/base/AbstractRewards.sol#L126)

```solidity
/**
  * @dev Increases or decreases the points correction for `account` by
  * `shares*pointsPerShare`.
  */
function _correctPoints(address _account, int256 _shares) internal {
  pointsCorrection[_account] = pointsCorrection[_account] + (_shares * (int256(pointsPerShare)));
}
```

## Tool used

Manual review

## Recommendation


_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-merit-circle-judging/issues/46_
