# [M] ERC20 transfer used for arbitrary tokens can fail silently

## Summary
Severity: Medium
Reporter: yixxas
Source: https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L418-L425
Type: audit-issue

## Details
# ERC20 transfer used for arbitrary tokens can fail silently

## Summary
Tokens like ZRX returns `false` on failure instead of reverting. This means that `_multiSwap()` will fail to catch this fail in transfer.

## Vulnerability Detail
`IERC20(midToken[i]).transfer(curPoolInfo.adapter, curAmount)` and `IERC20(midToken[i]).transfer(curPoolInfo.pool, curAmount)` are not handling the non-compliant tokens such as ZRX since `transfer` is used.

## Impact
Since token transfers are not caught on failure, an attacker can possibly abuse this fact and trick the protocol.

## Code Snippet
https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L418-L425

## Tool used

Manual Review

## Recommendation
Use OZ's safeTransfer instead to handle arbitrary ERC20 tokens.
