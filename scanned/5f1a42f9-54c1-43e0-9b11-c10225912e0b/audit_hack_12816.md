# [M] Instead Of `trasfer()` or `transferFrom()` Use `safeTransfer()` or `safeTransferFrom()`

## Summary
Severity: Medium
Reporter: 0xhacksmithh
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/TrailingStopDex.vy#L189
Type: audit-issue

## Details
# Instead Of `trasfer()` or `transferFrom()` Use `safeTransfer()` or `safeTransferFrom()`

## Summary
Should use `safeTransfer()` or `safeTransferFrom()`

## Vulnerability Detail
Some tokens does not revert on failure instead they return false, Their should always a return check.
Otherwise function consider to be `success` even on `failure`

```solidity
 ERC20(order.token_out).transfer(order.account, order.min_amount_out)
```


## Impact
Some tokens does not revert on failure instead they return false

## Code Snippet
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/TrailingStopDex.vy#L189
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/LimitOrders.vy#L188

## Tool used

Manual Review

## Recommendation
Should use `safeTransfer()` or `safeTransferFrom()`
