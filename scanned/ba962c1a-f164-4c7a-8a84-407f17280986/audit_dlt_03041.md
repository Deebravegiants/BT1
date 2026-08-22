# [M] Single UniswapV3Swapper using a single fee makes it highly likely to be suboptimal

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-07-tapioca
Published: 2023-08-04
Source: https://github.com/code-423n4/2023-07-tapioca-findings/issues/1553
Type: code-finding

## Details
# Lines of code

https://github.com/Tapioca-DAO/tapioca-yieldbox-strategies-audit/blob/05ba7108a83c66dada98bc5bc75cf18004f2a49b/contracts/stargate/StargateSwapperV3.sol#L94-L104
https://github.com/Tapioca-DAO/tapioca-periph-audit/blob/023751a4e987cf7c203ab25d3abba58f7344f213/contracts/Swapper/UniswapV3Swapper.sol#L180-L192


# Vulnerability details

### Impact
The `UniswapV3Swapper` uses a hardcoded `poolFee` instead of checking the chain for the best option (For both Stargate and in general)

https://github.com/Tapioca-DAO/tapioca-yieldbox-strategies-audit/blob/05ba7108a83c66dada98bc5bc75cf18004f2a49b/contracts/stargate/StargateSwapperV3.sol#L94-L104

https://github.com/Tapioca-DAO/tapioca-periph-audit/blob/023751a4e987cf7c203ab25d3abba58f7344f213/contracts/Swapper/UniswapV3Swapper.sol#L180-L192

```solidity
        ISwapRouter.ExactInputSingleParams memory params = ISwapRouter
            .ExactInputSingleParams({
                tokenIn: tokenIn,
                tokenOut: tokenOut,
                fee: poolFee, /// @audit MED - Pool Fee hardcoded exposes Swaps to suboptimal routes in most cases
                recipient: swapData.yieldBoxData.depositToYb
                    ? address(this)
                    : to,
                deadline: deadline,
                amountIn: amountIn,
                amountOutMinimum: amountOutMin,
                sqrtPriceLimitX96: 0
            });
```

Fees liquidity and price can change and fees are unique to type of pairs.

For highly liquid pairs, such as WETH and wBTC, low fees are best, while for more exotic pairs, such as CRV or AAVE, higher fees may be necessary

Limiting the swapper to a single fee tier can cause a significant loss on each swap

### Examples

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-07-tapioca-findings/issues/1553_
