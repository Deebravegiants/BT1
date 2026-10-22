# [M] PerpDepository._rebalanceNegativePnlWithSwap()

## Summary
Severity: Medium
Contest weight: 0.4416
Dataset id: 19801
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
PerpDepository._rebalanceNegativePnlWithSwap() shouldn't use a sqrtPriceLimitX96 twice.
Currently, _rebalanceNegativePnlWithSwap() uses a sqrtPriceLimitX96 param twice for placing a perp order and swapping.
```solidity
function _rebalanceNegativePnlWithSwap(
    uint256 amount,
    uint256 amountOutMinimum,
    uint160 sqrtPriceLimitX96,
    uint24 swapPoolFee,
    address account
) private returns (uint256, uint256) {
    uint256 normalizedAmount = amount.fromDecimalToDecimal(
        ERC20(quoteToken).decimals(),
    );
    _checkNegativePnl(normalizedAmount);
    bool isShort = false;
    bool amountIsInput = true;

    normalizedAmount,
    isShort,
    amountIsInput,
    sqrtPriceLimitX96
);
    vault.withdraw(assetToken, baseAmount);
    SwapParams memory params = SwapParams({
        tokenIn: assetToken,
        tokenOut: quoteToken,
        amountIn: baseAmount,
        amountOutMinimum: amountOutMinimum,
        poolFee: swapPoolFee
    });
```
In _placePerpOrder(), it uses the uniswap pool inside the perp protocol and uses a spotSwapper for the second swap which is for the uniswap as well.
But as we can see here, Uniswap V3 introduces multiple pools for each token pair and 2 pools might be different and I think it's not good to use the same sqrtPriceLimitX96 for different pools.
Also, I think it's not mandatory to check a sqrtPriceLimitX96 as it checks amountOutMinimum already. (It checks amountOutMinimum only in _openLong() and _openShort().)
PerpDepository._rebalanceNegativePnlWithSwap() might revert when it should work as it uses the same sqrtPriceLimitX96 for different pools.

## Recommendation
I think we can use the sqrtPriceLimitX96 param for one pool only and it would be enough as there is an amountOutMinimum condition.
