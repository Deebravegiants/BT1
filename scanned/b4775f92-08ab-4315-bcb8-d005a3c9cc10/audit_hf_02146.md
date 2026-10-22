# [H] Improved Logic on EvryPair::swap()

## Summary
Severity: High
Contest weight: 0.6359
Dataset id: 12028
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Evrynet protocol has the built-in DEX functionality that is inspired from UniswapV2, but with the extension of flexible support for reconfigurable trading fee and protocol fee. Both fees can be dynamically configured via the EvryFactory contract on current pool pairs. In the analysis of the core swap() logic, we notice the current implementation needs to be improved. To elaborate, we show below the swap() routine inside the evry-finance-amm-swap repository. This function is designed to perform the actual swap between the related two tokens, i.e., token0 and token1. Our analysis shows that the current logic can be improved in the following two aspects. Firstly, the fee collection is only performed in one side, but not both. In particular, the current logic examines the input amount amount0In. If it is positive, the helper routine sendFeeToPlatform() is called to collect the token0-side protocol fee. Otherwise, the token1-side protocol fee will be collected. However, in a flashswap scenario, it is possible both amount0In and amount1In are positive, which means the protocol fee collection needs to be performed in both sides.
```solidity
// this low-level function should be called from a contract which performs important safety checks
function swap(
    uint[2] memory amountOut,
    address to,
    address feeToPlatform,
    uint feePlatformBasis,
    uint feeLiquidityBasis,
    bytes calldata data
) external lock override {
    FeeConfiguration memory feeConfiguration = FeeConfiguration({
        feeToPlatform: feeToPlatform,
        feePlatformBasis: feePlatformBasis,
        feeLiquidityBasis: feeLiquidityBasis,
        amount0Out: amountOut[0],
        amount1Out: amountOut[1]
    });
    require(
        feeConfiguration.amount0Out > 0 || feeConfiguration.amount1Out > 0,
        " Evry:INSUFFICIENT_OUTPUT_AMOUNT"
    );
    (uint112 _reserve0, uint112 _reserve1,) = getReserves();
    // gas savings
    require(
        feeConfiguration.amount0Out < _reserve0 && feeConfiguration.amount1Out < _reserve1,
        " Evry: INSUFFICIENT_LIQUIDITY"
    );
    uint balance0;
    uint balance1;
    { // scope for _token{0,1}, avoids stack too deep errors
        address _token0 = token0;
        address _token1 = token1;
        require(
            to != _token0 && to != _token1,
            " Evry: INVALID_TO"
        );
        if (feeConfiguration.amount0Out > 0)
            _safeTransfer(_token0, to, feeConfiguration.amount0Out);
        // optimistically transfer tokens
        if (feeConfiguration.amount1Out > 0)
            _safeTransfer(_token1, to, feeConfiguration.amount1Out);
        // optimistically transfer tokens
        if (data.length > 0)
            IEvryCallee(to).evryCall(msg.sender, feeConfiguration.amount0Out, feeConfiguration.amount1Out, data);
        balance0 = IERC20(_token0).balanceOf(address(this));
        balance1 = IERC20(_token1).balanceOf(address(this));
    }
    uint amount0In = balance0 > _reserve0 - feeConfiguration.amount0Out ?
        balance0 - (_reserve0 - feeConfiguration.amount0Out) : 0;
    uint amount1In = balance1 > _reserve1 - feeConfiguration.amount1Out ?
        balance1 - (_reserve1 - feeConfiguration.amount1Out) : 0;
    require(
        amount0In > 0 || amount1In > 0,
        " Evry: INSUFFICIENT_INPUT_AMOUNT"
    );
    { // scope for reserve{0,1}Adjusted, avoids stack too deep errors
        uint totalFee = feeConfiguration.feePlatformBasis.add(feeConfiguration.feeLiquidityBasis);
        uint balance0Adjusted = balance0.mul(10000).sub(amount0In.mul(totalFee));
        uint balance1Adjusted = balance1.mul(10000).sub(amount1In.mul(totalFee));
        require(
            balance0Adjusted.mul(balance1Adjusted) >= uint(_reserve0).mul(_reserve1).mul(10000**2),
            " Evry: K"
        );
        _update(balance0, balance1);
    }
    // emit Swap(msg.sender, amount0In, amount1In, amountOut, to);
    if (amount0In > 0)
        sendFeeToPlatform(
            token0,
            amount0In,
            feeConfiguration.feePlatformBasis,
            feeConfiguration.feeToPlatform
        );
    else
        sendFeeToPlatform(
            token1,
            amount1In,
            feeConfiguration.feePlatformBasis,
            feeConfiguration.feeToPlatform
        );
    _sync();
}
```
Secondly, the fee, including both trade fee and protocol fee, is collected according to the given input to the swap() function. However, the input cannot be trusted! In other words, the caller may intentionally craft the input to avoid paying any trade fee, which could seriously dis-incentivize the liquidity providers.

## Recommendation
Revise the above swap() routine to reliably collect trade fee and protocol fee.
