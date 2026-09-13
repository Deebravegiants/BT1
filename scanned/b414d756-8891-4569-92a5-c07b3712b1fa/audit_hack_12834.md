# [M] Protocol is not compatible with USDT

## Summary
Severity: Medium
Reporter: 0xDjango
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L204
Type: audit-issue

## Details
# Protocol is not compatible with USDT

## Summary
USDT requires approving an amount of `0` if a non-zero approval balance already exists to prevent against race conditions. Since Unstoppable does not perform an approve(0) prior to approve(amount), USDT will not be able to be used following the first approval.

## Vulnerability Detail
The well-known USDT approval bug can be found in the following function that approves UniV3 to swap the contract's tokens:

```solidity
    # approve UNISWAP_ROUTER to spend amount token_in
    ERC20(order.token_in).approve(UNISWAP_ROUTER, order.amount_in_per_execution)
```

## Impact
- Unable to use USDT with UniV3

## Code Snippet
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L204

## Tool used
Manual Review

## Recommendation
For each token approval, approve an amount of 0 prior to approving the real amount.
