# [M] Improved Validation Of Function Arguments

## Summary
Severity: Medium
Contest weight: 0.4597
Dataset id: 9
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the FireBirdRouter contract, we observe the _swapSingleSupportFeeOnTransferTokens() function is used to swap the exact amount of tokenIn to tokenOut. To elaborate, we show below the related code snippet. In the function, the FireBirdFormula::getFactoryReserveAndWeights() function is called (line 460) to acquire the current state of the pool which is a FireBirdPair instance that stores two different tokens address and the related info, including reserve0, reserve1, tokenWeight0, swapFee, and so on. These parameters of the pool will be used by FireBirdFormula::getAmountOut() (line 462) to calculate the amount of tokenOut swapped with the exact amount of tokenIn.  
In the FireBirdFormula::getFactoryReserveAndWeights() function, we notice if the third input argument tokenA is not equal to the token0 address in the pool specified by the second input argument pair, tokenA will be treated as token1 and the function will return the corresponding state of the pool. If tokenA is neither equal to token0, nor equal to token1, the function will return incorrect values, which may introduce unexpected behavior for those functions call it. We may need to validate tokenA is either equal to token0 or equal to token1 at the beginning of the function.  
```solidity
function _swapSingleSupportFeeOnTransferTokens(address tokenIn, address tokenOut, address pool, uint swapAmount, uint limitReturnAmount) internal returns(uint tokenAmountOut) {
    TransferHelper.safeTransfer(tokenIn, pool, swapAmount);
    uint amountOutput;
    (, uint reserveInput, uint reserveOutput, uint32 tokenWeightInput, uint32 tokenWeightOutput, uint32 swapFee) = IFireBirdFormula(formula).getFactoryReserveAndWeights(factory, pool, tokenIn);
    uint amountInput = IERC20(tokenIn).balanceOf(pool).sub(reserveInput);
    amountOutput = IFireBirdFormula(formula).getAmountOut(amountInput, reserveInput, reserveOutput, tokenWeightInput, tokenWeightOutput, swapFee);
    uint balanceBefore = IERC20(tokenOut).balanceOf(address(this));
    (uint amount0Out, uint amount1Out) = tokenIn == IFireBirdPair(pool).token0() ? (uint(0), amountOutput) : (amountOutput, uint(0));
    IFireBirdPair(pool).swap(amount0Out, amount1Out, address(this), new bytes(0));
    emit Exchange(pool, amountOutput, tokenOut);
    tokenAmountOut = IERC20(tokenOut).balanceOf(address(this)).sub(balanceBefore);
    require(tokenAmountOut >= limitReturnAmount, "Router: INSUFFICIENT_OUTPUT_AMOUNT");
}

function getFactoryReserveAndWeights(address factory, address pair, address tokenA)
    public
    override
    view
    returns (
        address tokenB,
        uint reserveA,
        uint reserveB,
        uint32 tokenWeightA,
        uint32 tokenWeightB,
        uint32 swapFee
    )
{
    address token0 = IFireBirdPair(pair).token0();
    (uint reserve0, uint reserve1,) = IFireBirdPair(pair).getReserves();
    uint32 tokenWeight0;
    uint32 tokenWeight1;
    (tokenWeight0, tokenWeight1, swapFee) = getFactoryWeightsAndSwapFee(factory, pair);
    if (tokenA == token0) {
        (tokenB, reserveA, reserveB, tokenWeightA, tokenWeightB) = (IFireBirdPair(pair).token1(), reserve0, reserve1, tokenWeight0, tokenWeight1);
    } else {
        (tokenB, reserveA, reserveB, tokenWeightA, tokenWeightB) = (token0, reserve1, reserve0, tokenWeight1, tokenWeight0);
    }
}
```
Note a number of functions can be similarly improved, including FireBirdFormula::getReserveAndWeights(), FireBirdFormula::getReserves() and FireBirdFormula::getOtherToken().

## Recommendation
Validate whether the token address is in the pair at the beginning of the functions.
