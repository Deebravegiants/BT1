# [H] _direct_swap() swaps have no slippage parameters

## Summary
Severity: High
Reporter: Darwin
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/SwapRouter.vy#L95
Type: audit-issue

## Details
# _direct_swap() swaps have no slippage parameters

## Summary
_direct_swap() swaps have no slippage parameters
## Vulnerability Detail
In [uniswap Doc](https://docs.uniswap.org/contracts/v3/guides/swaps/single-swaps) , if sqrtPriceLimitX96 is zero - which makes this parameter inactive.
## Impact
This value can be used to set the limit for the price the swap will push the pool to, which can help protect against price impact or for setting up logic in a variety of price-relevant mechanisms.
## Code Snippet
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/SwapRouter.vy#L95

## Tool used

Manual Review

## Recommendation

According to the [uniswapv3book](https://uniswapv3book.com/docs/milestone_3/slippage-protection/), to protect swaps, we need to add one more parameter to swap function–we want to let user choose a stop price, a price at which swapping will stop.
