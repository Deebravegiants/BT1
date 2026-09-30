# [M] Inconsistent Fee Share Calculation in QuantoSwapV2LiquidityMathLibrary

## Summary
Severity: Medium
Contest weight: 0.4400
Dataset id: 12821
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In this section, we examine a specific QuantoSwapV2LiquidityMathLibrary library that is designed to provide a number of convenience functions, e.g. computing their exact value in terms of the underlying tokens. Our analysis of this library exposes a specific function computeLiquidityValue() for improvement. To elaborate, we show below this computeLiquidityValue() routine. This routine implements a rather straightforward logic in computing the liquidity value given all six parameters of the pair, i.e., reservesA, reservesB, totalSupply, liquidityAmount, feeOn, and kLast. Notice that this routine uses 1/3 of collected swap fee for protocol fee while default 1/2 of collected swap fee, if turned on, will be collected for protocol fee.
```solidity
function computeLiquidityValue(
    uint256 reservesA,
    uint256 reservesB,
    uint256 totalSupply,
    uint256 liquidityAmount,
    bool feeOn,
    uint kLast
) internal
pure
returns (uint256 tokenAAmount, uint256 tokenBAmount) {
    if (feeOn && kLast > 0) {
        uint rootK = Babylonian.sqrt(reservesA.mul(reservesB));
        uint rootKLast = Babylonian.sqrt(kLast);
        if (rootK > rootKLast) {
            uint numerator1 = totalSupply;
            uint numerator2 = rootK.sub(rootKLast);
            uint denominator = rootK.mul(2).add(rootKLast);
            uint feeLiquidity = FullMath.mulDiv(numerator1, numerator2, denominator);
            totalSupply = totalSupply.add(feeLiquidity);
        }
    }
    return (reservesA.mul(liquidityAmount) / totalSupply, reservesB.mul(liquidityAmount) / totalSupply);
}
```

## Recommendation
Revise the above computeLiquidityValue() routine to be consistent in collecting the percentage of swap fee for protocol fee.
