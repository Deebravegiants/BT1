# [M] UniswapV3RouterUpgradeable::exactInputETHForTokens

## Summary
Severity: Medium
Contest weight: 0.4219
Dataset id: 22467
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
UniswapV3RouterUpgradeable::exactInputETHForTokens does not check whether the received amount is greater than or equal to amountOutMin. When a swap is done through UniswapV3RouterUpgradeable::exactInputETHForTokens, it is expected that the account should receive at least the amountOutMin specified in the parameters:
```solidity
function exactInputETHForTokens(
    uint256 amountOutMin,
    address tokenOut,
    uint24 poolFee,
    uint256 feeBips,
    uint256 deadline,
    uint256 ethAmountToCoinbase
)
    tokens.
    (int256 amount0, int256 amount1) = IUniswapV3Pool(poolAddress).swap(
        msg.sender,
        zeroForOne,
        SafeCast.toInt256(amountIn),
        zeroForOne ? MIN_SQRT_RATIO + 1 : MAX_SQRT_RATIO - 1,
        abi.encode(SwapCallbackData(WETH, tokenOut, address(this), poolFee))
    );
    actualAmountIn = uint256(zeroForOne ? amount0 : amount1);
    amountOut = uint256(-(zeroForOne ? amount1 : amount0));
    require(amountOut >= amountOutMin, "INSUFFICIENT_OUTPUT_AMOUNT");
```
This just checks the result of the swap function instead of checking the recipient's balance before and after the swap. The recipient can receive less than the minimum amount they specified translating to a loss of funds.

## Recommendation
Add a check to ensure that the change in balance of the recipient before and after the swap is greater than the minimum output amount they specified.
