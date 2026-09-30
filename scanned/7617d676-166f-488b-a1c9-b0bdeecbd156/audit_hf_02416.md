# [H] Trading Fee Discrepancy Between ShibaSwap And ShibaNova

## Summary
Severity: High
Contest weight: 0.6362
Dataset id: 12987
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
As a decentralized exchange and automatic market maker, the ShibaNova protocol has a constant need to convert one token to another. With the built-in ShibaSwap, if you make a token swap or trade on the exchange, you will need to pay a 0.2% trading fee, which is split into two parts. The ﬁrst part is returned to liquidity pools in the form of a fee reward for liquidity providers while the second part is sent to the feeManager for distribution.

To elaborate, we show below the getAmountOut() routine inside the the ShibaLibrary. For com-parison, we also show the swap() routine in ShibaPair. It is interesting to note that ShibaPair has implicitly assumed the trading fee is 0.2%, instead of 0.16% in ShibaLibrary. The diﬀerence in the built-in trading fee may deviate the normal operations of a number of helper routines in ShibaRouter.
```solidity
// given an input amount of an asset and pair reserves, returns the maximum output amount of the other asset
function getAmountOut(uint amountIn, uint reserveIn, uint reserveOut) internal pure returns (uint amountOut) {
    require(amountIn > 0, "ShibaLibrary: INSUFFICIENT_INPUT_AMOUNT");
    require(reserveIn > 0 && reserveOut > 0, "ShibaLibrary: INSUFFICIENT_LIQUIDITY");
    uint amountInWithFee = amountIn.mul(9984);
    uint numerator = amountInWithFee.mul(reserveOut);
    uint denominator = reserveIn.mul(10000).add(amountInWithFee);
    amountOut = numerator / denominator;
}
// given an output amount of an asset and pair reserves, returns a required input amount of the other asset
function getAmountIn(uint amountOut, uint reserveIn, uint reserveOut) internal pure returns (uint amountIn) {
    require(amountOut > 0, "ShibaLibrary: INSUFFICIENT_OUTPUT_AMOUNT");
    require(reserveIn > 0 && reserveOut > 0, "ShibaLibrary: INSUFFICIENT_LIQUIDITY");
    uint numerator = reserveIn.mul(amountOut).mul(10000);
    uint denominator = reserveOut.sub(amountOut).mul(9984);
    amountIn = (numerator / denominator).add(1);
}
function swap(uint amount0Out, uint amount1Out, address to, bytes calldata data) external lock {
    require(amount0Out > 0 || amount1Out > 0, "ShibaSwap: INSUFFICIENT_OUTPUT_AMOUNT");
    (uint112 _reserve0, uint112 _reserve1,) = getReserves(); // gas savings
    require(amount0Out < _reserve0 && amount1Out < _reserve1, "ShibaSwap: INSUFFICIENT_LIQUIDITY");
    uint balance0;
    uint balance1;
    { // scope for _token{0,1}, avoids stack too deep errors
        address _token0 = token0;
        address _token1 = token1;
        require(to != _token0 && to != _token1, "ShibaSwap: INVALID_TO");
        if (amount0Out > 0)
            _safeTransfer(_token0, to, amount0Out); // optimistically transfer tokens
        if (amount1Out > 0)
            _safeTransfer(_token1, to, amount1Out); // optimistically transfer tokens
        if (data.length > 0)
            IShibaCallee(to).shibaCall(msg.sender, amount0Out, amount1Out, data);
        balance0 = IERC20(_token0).balanceOf(address(this));
        balance1 = IERC20(_token1).balanceOf(address(this));
        uint amount0In = balance0 > _reserve0 - amount0Out ? balance0 - (_reserve0 - amount0Out) : 0;
        uint amount1In = balance1 > _reserve1 - amount1Out ? balance1 - (_reserve1 - amount1Out) : 0;
        require(amount0In > 0 || amount1In > 0, "ShibaSwap: INSUFFICIENT_INPUT_AMOUNT");
        { // scope for reserve{0,1}Adjusted, avoids stack too deep errors
            uint balance0Adjusted = balance0.mul(10000).sub(amount0In.mul(20));
            uint balance1Adjusted = balance1.mul(10000).sub(amount1In.mul(20));
            require(balance0Adjusted.mul(balance1Adjusted) >= uint(_reserve0).mul(_reserve1).mul(10000**2), "ShibaSwap: K");
        }
        _update(balance0, balance1, _reserve0, _reserve1);
        emit Swap(msg.sender, amount0In, amount1In, amount0Out, amount1Out, to);
    }
}
```

## Recommendation
Make the built-in trading fee in ShibaNova consistent with the actual trading fee in ShibaPair.
