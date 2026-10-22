# [M] Inconsistent Fee Rate Used in DaoSwap

## Summary
Severity: Medium
Contest weight: 0.4598
Dataset id: 12949
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In SatoshiIncognito DaoSwap, there is a DAOLibrary contract which provides a pair of interfaces (i.e., getAmountIn()/getAmountOut()) to facilitate users trading. While reviewing the swap fee rate used in the two interfaces, we notice it is inconsistent with the one used in the swap() and the inconsistency needs to be resolved.
To elaborate, we show below the code snippet of the getAmountIn()/getAmountOut()/swap() routines. As the name indicates, the getAmountIn() routine accepts an input amount of an asset and pair reserves, and returns the maximum output amount of the other asset. The getAmountOut() counterpart accepts an output amount of an asset and pair reserves, and returns a required input amount of the other asset. The fee rate used in these two routines is 3/1000 (lines 47 and 58). However, in the swap() routine which implements the trading, the fee rate used is 25/10000 (lines 198 and 199).
Due to the inconsistent fee rates, the user may not get the expected amount of asset from the swap or the getAmountIn()/getAmountOut() routines may not return the correct token amount to the user.
```solidity
// given an input amount of an asset and pair reserves, returns the maximum output amount of the other asset
function getAmountOut(uint amountIn, uint reserveIn, uint reserveOut) internal pure returns (uint amountOut) {
    require(amountIn > 0, "DAOLibrary: INSUFFICIENT_INPUT_AMOUNT");
    require(reserveIn > 0 && reserveOut > 0, "DAOLibrary: INSUFFICIENT_LIQUIDITY");
    uint amountInWithFee = amountIn.mul(9970);
    uint numerator = amountInWithFee.mul(reserveOut);
    uint denominator = reserveIn.mul(10000).add(amountInWithFee);
    amountOut = numerator / denominator;
}
// given an output amount of an asset and pair reserves, returns a required input amount of the other asset
function getAmountIn(uint amountOut, uint reserveIn, uint reserveOut) internal pure returns (uint amountIn) {
    require(amountOut > 0, "DAOLibrary: INSUFFICIENT_OUTPUT_AMOUNT");
    require(reserveIn > 0 && reserveOut > 0, "DAOLibrary: INSUFFICIENT_LIQUIDITY");
    uint numerator = reserveIn.mul(amountOut).mul(10000);
    uint denominator = reserveOut.sub(amountOut).mul(9970);
    amountIn = (numerator / denominator).add(1);
}

function swap(uint amount0Out, uint amount1Out, address to) external lock {
    require(amount0Out > 0 || amount1Out > 0, "DAO: INSUFFICIENT_OUTPUT_AMOUNT");
    (uint112 _reserve0, uint112 _reserve1,) = getReserves(); // gas savings
    require(amount0Out < _reserve0 && amount1Out < _reserve1, "DAO: INSUFFICIENT_LIQUIDITY");
    uint balance0;
    uint balance1;
    {// scope for _token{0,1}, avoids stack too deep errors
        address _token0 = token0;
        address _token1 = token1;
        require(to != _token0 && to != _token1, "DAO: INVALID_TO");
        if (amount0Out > 0)
            _safeTransfer(_token0, to, amount0Out); // optimistically transfer tokens
        if (amount1Out > 0)
            _safeTransfer(_token1, to, amount1Out); // optimistically transfer tokens
        // remove flash swap
        // if (data.length > 0)
        // IDAOCallee(to).daoCall(msg.sender, amount0Out, amount1Out, data);
        balance0 = IERC20(_token0).balanceOf(address(this));
        balance1 = IERC20(_token1).balanceOf(address(this));
    }
    uint amount0In = balance0 > _reserve0 - amount0Out ? balance0 - (_reserve0 - amount0Out) : 0;
    uint amount1In = balance1 > _reserve1 - amount1Out ? balance1 - (_reserve1 - amount1Out) : 0;
    require(amount0In > 0 || amount1In > 0, "DAO: INSUFFICIENT_INPUT_AMOUNT");
    {// scope for reserve{0,1}Adjusted, avoids stack too deep errors
        uint balance0Adjusted = (balance0.mul(10000).sub(amount0In.mul(25)));
        uint balance1Adjusted = (balance1.mul(10000).sub(amount1In.mul(25)));
        require(balance0Adjusted.mul(balance1Adjusted) >= uint(_reserve0).mul(_reserve1).mul(10000**2), "DAO: K");
    }
    _update(balance0, balance1, _reserve0, _reserve1);
    emit Swap(msg.sender, amount0In, amount1In, amount0Out, amount1Out, to);
}
```

## Recommendation
Revisit the above mentioned routines to use the same swap fee rate in the whole protocol.
