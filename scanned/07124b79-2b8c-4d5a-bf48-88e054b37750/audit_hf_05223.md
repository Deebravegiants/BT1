# [M] CompensationPriceFinder::getZeroForOne may compute smaller effective prices than expected

## Summary
Severity: Medium
Contest weight: 0.0000
Dataset id: 23372
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
CompensationPriceFinder::getOneForZero contains a conditional branch that exists to skip execution that would result in reverts either due to underflow or division by zero:
```solidity
if (sumAmount0Deltas > taxInEther) {
    uint256 simplePstarX96 = sumAmount1Deltas.divX96(sumAmount0Deltas - taxInEther);
    if (simplePstarX96 <= uint256(priceUpperSqrtX96).mulX96(priceUpperSqrtX96)) {
        pstarSqrtX96 = _oneForZeroGetFinalCompensationPrice(...);
        return (lastTick, pstarSqrtX96);
    }
}
```
This logic is also present in CompensationPriceFinder::getZeroForOne; however, in this case, neither underflow nor division by zero is possible:
```solidity
if (sumAmount0Deltas > taxInEther) {
    if (
        sumAmount1Deltas.divX96(sumAmount0Deltas + taxInEther)
        >= uint256(priceLowerSqrtX96).mulX96(priceLowerSqrtX96)
    ) {
        pstarSqrtX96 = _zeroForOneGetFinalCompensationPrice(...);
        return (lastTick, pstarSqrtX96);
    }
}
```
This could result in the effective price calculation being skipped even when it would have been validated to lie within the current tick range, since the threshold ratio could be satisfied even when `sumAmount0Deltas <= taxInEther`.  
Furthermore, after all the ticks have been iterated, there is a subsequent asymmetry when checking the effective price condition:
```solidity
if (simplePstarX96 > uint256(priceLowerSqrtX96).mulX96(priceLowerSqrtX96)) {
```
Here, if the effective price is exactly equal to the end tick then execution will fall through to returning a 512-bit square root price based on `simplePstarX96` instead of executing `_oneForZeroGetFinalCompensationPrice()`.

Impact: This may result in computation of a smaller effective price than expected, compensating liquidity providers who otherwise shouldn't be compensated.

## Recommendation
```solidity
function getZeroForOne(
    TickIteratorDown memory ticks,
    uint128 liquidity,
    uint256 taxInEther,
    uint160 priceUpperSqrtX96,
    Slot0 slot0AfterSwap
) internal view returns (int24 lastTick, uint160 pstarSqrtX96) {
    uint256 sumAmount0Deltas = 0; // X
    uint256 sumAmount1Deltas = 0; // Y
    uint160 priceLowerSqrtX96;
    while (ticks.hasNext()) {
        lastTick = ticks.getNext();
        priceLowerSqrtX96 = TickMath.getSqrtPriceAtTick(lastTick);
        {
            uint256 delta0 = SqrtPriceMath.getAmount0Delta(
                priceLowerSqrtX96, priceUpperSqrtX96, liquidity, false
            );
            uint256 delta1 = SqrtPriceMath.getAmount1Delta(
                priceLowerSqrtX96, priceUpperSqrtX96, liquidity, false
            );
            sumAmount0Deltas += delta0;
            sumAmount1Deltas += delta1;
            // if (sumAmount0Deltas > taxInEther) {
            if (sumAmount0Deltas > taxInEther) {
                if (
                    sumAmount1Deltas.divX96(sumAmount0Deltas + taxInEther)
                    >= uint256(priceLowerSqrtX96).mulX96(priceLowerSqrtX96)
                ) {
                    pstarSqrtX96 = _zeroForOneGetFinalCompensationPrice(
                        priceUpperSqrtX96,
                        taxInEther,
                        liquidity,
                        sumAmount0Deltas - delta0,
                        sumAmount1Deltas - delta1
                    );
                    return (lastTick, pstarSqrtX96);
                }
            }
        }
        (, int128 liquidityNet) = ticks.manager.getTickLiquidity(ticks.poolId, lastTick);
        require(int128(liquidity) >= liquidityNet, "getZeroForOne: liquidity < liquidityNet");
        liquidity = liquidity.sub(liquidityNet);
        priceUpperSqrtX96 = priceLowerSqrtX96;
    }
    priceLowerSqrtX96 = slot0AfterSwap.sqrtPriceX96();
    uint256 delta0 =
        SqrtPriceMath.getAmount0Delta(priceLowerSqrtX96, priceUpperSqrtX96, liquidity, false);
    uint256 delta1 =
        SqrtPriceMath.getAmount1Delta(priceLowerSqrtX96, priceUpperSqrtX96, liquidity, false);
    sumAmount0Deltas += delta0;
    sumAmount1Deltas += delta1;
    uint256 simplePstarX96 = sumAmount1Deltas.divX96(sumAmount0Deltas + taxInEther);
    // if (simplePstarX96 > uint256(priceLowerSqrtX96).mulX96(priceLowerSqrtX96)) {
    if (simplePstarX96 >= uint256(priceLowerSqrtX96).mulX96(priceLowerSqrtX96)) {
        pstarSqrtX96 = _zeroForOneGetFinalCompensationPrice(
            priceUpperSqrtX96,
            taxInEther,
            liquidity,
            sumAmount0Deltas - delta0,
            sumAmount1Deltas - delta1
        );
        return (type(int24).min, pstarSqrtX96);
    }
    (uint256 p1, uint256 p0) = Math512Lib.checkedMul2Pow96(0, simplePstarX96);
    return (type(int24).min, Math512Lib.sqrt512(p1, p0).toUint160());
}
```
