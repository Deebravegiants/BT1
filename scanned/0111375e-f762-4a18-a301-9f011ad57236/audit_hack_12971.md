# [H] Where `SqrtPriceX96` is set to Zero, the swap logic is completely broken.

## Summary
Severity: High
Reporter: shealtielanz
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/TrailingStopDex.vy#L177C4-L184C29
Type: audit-issue

## Details
# Where `SqrtPriceX96` is set to Zero, the swap logic is completely broken.

## Summary
The `TrailingStopDex.vy` and `SwapRouter.vy` go In the context of the `Uniswap v3` protocol, where  `sqrtPriceLimitX96` is a parameter that helps limit the price range within which a liquidity provider's funds can be used. Setting `sqrtPriceLimitX96` to zero can have significant consequences
## Vulnerability Detail
In `SwapRouter.vy` 
```vyper
    uni_params: ExactInputSingleParams = ExactInputSingleParams({
        tokenIn: order.token_in,
        tokenOut: order.token_out,
        fee: _uni_pool_fee,
        recipient: self,
        deadline: order.valid_until,
        amountIn: order.amount_in,
        amountOutMinimum: order.min_amount_out,
        sqrtPriceLimitX96: 0
    })
```
In `TrailingStopDex.vy`
```vyper
        tokenIn: order.token_in,
        tokenOut: order.token_out,
        fee: _uni_pool_fee,
        recipient: self,
        deadline: order.valid_until,
        amountIn: order.amount_in,
        amountOutMinimum: order.min_amount_out,
        sqrtPriceLimitX96: 0
```
You can see that the `sqrtPriceLimitX96` is aet to zero in both scenarios.
## Impact
When `sqrtPriceLimitX96` is set to zero, it effectively removes any constraints on the price range, meaning swaps can go at any price allowing for extreme price movements and loss of control over slippage, thereby rendering the `swap logic` completely broken.
## Code Snippet
- https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/TrailingStopDex.vy#L177C4-L184C29
- https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/SwapRouter.vy#L88C8-L95C34
## Tool used

Manual Review

## Recommendation
get the `SqrtPriceX96` via `TWAP`.
