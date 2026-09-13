# [M] `SwapRouter.vy` requires users to swap all tokens through same router and hardcoded paths

## Summary
Severity: Medium
Reporter: Breeje
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/SwapRouter.vy#L111-L120
Type: audit-issue

## Details
# `SwapRouter.vy` requires users to swap all tokens through same router and hardcoded paths

## Summary

`SwapRouter.vy` requires users to swap tokens through same router. Also the swap paths are hardcoded which might not be optimal. This is problematic as it is very unlikely that a UniswapV3 router will have good liquidity sources for all tokens and will result in users experiencing forced losses to their token.

## Vulnerability Detail

```solidity
File: SwapRouter.vy

    uni_params: ExactInputParams = ExactInputParams(
        {
 @->        path: path,    // @audit-issue hardcoded path
            recipient: msg.sender,
            deadline: block.timestamp,
            amountIn: _amount_in,
            amountOutMinimum: _min_amount_out,
        }
    )
    return UniswapV3SwapRouter(UNISWAP_ROUTER).exactInput(uni_params)

```
[Link to Code](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/SwapRouter.vy#L111-L120)

All tokens are forcibly swapped through a single router using the hardcoded path value.

## Impact

Users will be forced to swap through a router with hardcoded path even if it doesn't have good liquidity for all tokens or the path is not optimal.

## Code Snippet

Shown Above.

## Tool used

Manual Review

## Recommendation

Allow users to use an aggregator like paraswap or multiple routers instead of only one single UniswapV3 router. Also allow users to add their optimal Path based on the Pool conditions through function parameters rather than always using the hardcoded ones.
