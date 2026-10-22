# [H] Incorrect K-Invariant Enforcement in UniswapV2Pair

## Summary
Severity: High
Contest weight: 0.6371
Dataset id: 12312
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The JanisDex protocol is a fork of the popular UniswapV2 protocol with fee adjustment as well as other features. While examining the impact on the enforced K-Invariant due to the fee adjustment, we notice the invariant is not properly enforced. To elaborate, we show below the related UniswapV2Pair::swap() routine. As the name indicates, this routine performs the actual swap logic with the enforcement of K-Invariant. However, it comes to our attention that the current enforcement (line 223) mis-calculates the precision and may be exploited to drain funds from the pair. The correct enforcement should be the following: require(balance0Adjusted.mul(balance1Adjusted) >= uint(_reserve0).mul(_reserve1).mul(10000**2)!
```solidity
function swap(uint amount0Out, uint amount1Out, address to, bytes calldata data) external lock {
    require(amount0Out > 0 || amount1Out > 0, "UniswapV2: INSUFFICIENT_OUTPUT_AMOUNT");
    (uint112 _reserve0, uint112 _reserve1,) = getReserves(); // gas savings
    require(amount0Out < _reserve0 && amount1Out < _reserve1, "UniswapV2: INSUFFICIENT_LIQUIDITY");

    uint balance0;
    uint balance1;
    { // scope for _token{0,1}, avoids stack too deep errors
        address _token0 = token0;
        address _token1 = token1;
        require(to != _token0 && to != _token1, "UniswapV2: INVALID_TO");

        if (amount0Out > 0) _safeTransfer(_token0, to, amount0Out); // optimistically transfer tokens
        if (amount1Out > 0) _safeTransfer(_token1, to, amount1Out); // optimistically transfer tokens
        if (data.length > 0) IUniswapV2Callee(to).uniswapV2Call(msg.sender, amount0Out, amount1Out, data);
        balance0 = IERC20Uniswap(_token0).balanceOf(address(this));
        balance1 = IERC20Uniswap(_token1).balanceOf(address(this));
    }

    uint amount0In = balance0 > _reserve0 - amount0Out ? balance0 - (_reserve0 - amount0Out) : 0;
    uint amount1In = balance1 > _reserve1 - amount1Out ? balance1 - (_reserve1 - amount1Out) : 0;
    require(amount0In > 0 || amount1In > 0, "UniswapV2: INSUFFICIENT_INPUT_AMOUNT");

    { // scope for reserve{0,1}Adjusted, avoids stack too deep errors
        uint _swapFee = swapFee;
        uint balance0Adjusted = (balance0.mul(10000).sub(amount0In.mul(_swapFee)));
        uint balance1Adjusted = (balance1.mul(10000).sub(amount1In.mul(_swapFee)));
        require(balance0Adjusted.mul(balance1Adjusted) >= uint(_reserve0).mul(_reserve1).mul(1000**2), "UniswapV2: K");
    }

    _update(balance0, balance1, _reserve0, _reserve1);
    emit Swap(msg.sender, amount0In, amount1In, amount0Out, amount1Out, to);
}
```

## Recommendation
Revise the above logic to properly enforce the K-Invariant. Note that the same issue is also present in the library UniswapV2Library.
