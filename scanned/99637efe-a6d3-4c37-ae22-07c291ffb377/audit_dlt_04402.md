# [M] `safeApprove` is front-runnable

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-sentiment
Published: 2022-11-04
Source: https://github.com/sherlock-audit/2022-11-sentiment-judging/issues/25
Type: sherlock-finding

## Details
Tomo

medium

# `safeApprove` is front-runnable

## Summary
`safeApproe` is front-runnable

## Vulnerability Detail
``` solidity
/**
 * @dev Deprecated. This function has issues similar to the ones found in
 * {IERC20-approve}, and its usage is discouraged.
 *
 * Whenever possible, use {safeIncreaseAllowance} and
 * {safeDecreaseAllowance} instead.
 */
```
Ref: https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/token/ERC20/utils/SafeERC20.sol#L39-L45

``` solidity
// safeApprove should only be called when setting an initial allowance,
// or when resetting it to zero. To increase and decrease it, use
// 'safeIncreaseAllowance' and 'safeDecreaseAllowance'
```
Ref: https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/token/ERC20/utils/SafeERC20.sol#L51-L53

By the [`SafeERC20.sol`](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/token/ERC20/utils/SafeERC20.sol) of OpenZeppelin, `safeApprove()` is deprecated due to it has the vulnerability.

This attack pattern is as follows.

### Example
- Eve has 100 allowances from `AccountManager`.

Now the `AccountManager` decide to change the approval of Eve from 100 to 50. 

Eve detects the transaction the `safeApprove(address(Eve),50)` from `AccountManager`

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-sentiment-judging/issues/25_
