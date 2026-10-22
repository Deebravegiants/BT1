# [M] routeFeeRate being set to 0 can break the protocol for certain tokens

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-dodo
Published: 2022-11-15
Source: https://github.com/sherlock-audit/2022-11-dodo-judging/issues/54
Type: sherlock-finding

## Details
yixxas

medium

# routeFeeRate being set to 0 can break the protocol for certain tokens

## Summary
Some ERC20 tokens revert when a `0 value` is attempted to be transferred. Fees are paid by tokens in which swaps are made into and transferred with `IERC20(toToken).universalTransfer(payable(routeFeeReceiver), routeFee)`. If `routeFeeRate` is set to 0, it can prevent swaps for being done on such tokens.

## Vulnerability Detail
`routeFeeRate` is initially set at 1e15 but can be changed with `changeRouteFeeRate()` and there is no minimum on fee rate set. Should `routeFeeRate` be set to 0, it can cause a revert when `_routeWithdraw()` is called, which every swap function uses. This prevents swaps of `toToken` being such tokens.

## Impact
`routeFeeRate` being set to 0 can prevent protocol to do swaps for certain tokens. This is problematic during production as this bug happens only to swaps for certain tokens, and it may not be easy to figure out the underlying problem causing this.

## Code Snippet
https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L130
https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L478-L479

## Tool used

Manual Review

## Recommendation
Disallow fee from being set to 0, or make the change in `_routeWithdraw()` such that fee is transferred only when `routeFee > 0`.
**Note that `brokerFee` faces the same issue and should implement the same fix**.
