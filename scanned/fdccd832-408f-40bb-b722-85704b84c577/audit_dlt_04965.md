# [H] `extendLock()` retroactively applies multiplier while `increaseLock()` doesnt

## Summary
Severity: High
Chain: Smart contract
Component: 2022-10-merit-circle
Published: 2022-10-14
Source: https://github.com/sherlock-audit/2022-10-merit-circle-judging/issues/87
Type: sherlock-finding

## Details
hickuphh3

high

# `extendLock()` retroactively applies multiplier while `increaseLock()` doesnt

## Summary
When calculating the new shares to be issued, `extendLock()` retroactively applies the multiplier to the existing amount, but `increaseLock()` does not. This inconsistency results in different calculations of shares.

## Vulnerability Detail
`increaseLock()` adds more deposits to the current lock. It calculates the new shares to be minted as:
```solidity
uint256 mintAmount = _increaseAmount * getMultiplier(remainingDuration) / 1e18;
```

Note that `mintAmount` is the additional amount of shares that the user is entitled to.

In contrast, the `mintAmount` calculated for `extendLock()` applies to the existing user amount, and seemingly rightfully so, since it is only the duration that changes.
```solidity
uint256 mintAmount = userDeposit.amount * getMultiplier(duration) / 1e18;
```

However, because the multiplier is only applied on the increased amount in `increaseLock()` and not the user's existing amount as well, we see that there will be a discrepancy in share calculations should the multiplier be changed.

### POC
0. Assume a constant multiplier of 1x regardless of duration: ie. 1:1 conversion of tokens to shares.
1. Alice and Bob perform deposits.
- Alice deposits 500 tokens for 1 year: 500 shares are minted
- Bob deposits 1000 tokens for 6 months: 1000 shares are minted
2. Assume the curve multiplier for 6 months changes to 3x.
2. After 6 months,
- Alice doubles her stake on her deposit: calls `increaseLock()` with 500 more tokens.
- Bob decides to extend his lock on his deposit for another 6 months: calls `extendLock()` with 6 months.

The end-result is expected to be the same: deposits of Alice and Bob should share the same state of 1000 tokens that are locked for a remaining / total duration of 6 months. However, the shares allocated for both deposit will differ.

#### Alice's Deposit
```solidity
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-merit-circle-judging/issues/87_
