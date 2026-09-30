# [M] UniswapV3Initializer.calculateLpTail() Miscalculates lpTailLiquidity Due to Incorrect Tick Usage

## Summary
Severity: Medium
Reporter: KupiaSec, also found by trachev and 0xacnologiac
Contest weight: 0.4603
Dataset id: 4619
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function calculateLpTail(
    uint16 id,
    int24 tickLower,
    int24 tickUpper,
    bool isToken0,
    uint256 reserves,
    uint256 bondingAssetsRemaining,
    int24 tickSpacing
) internal pure returns (LpPosition memory lpTail) {
    int24 tailTick = isToken0 ? tickUpper : tickLower;
    uint160 sqrtPriceAtTail = TickMath.getSqrtPriceAtTick(tailTick);
    uint128 lpTailLiquidity = LiquidityAmounts.getLiquidityForAmounts(
        sqrtPriceAtTail,
        TickMath.MIN_SQRT_PRICE,
        TickMath.MAX_SQRT_PRICE,
        isToken0 ? bondingAssetsRemaining : reserves,
        isToken0 ? reserves : bondingAssetsRemaining
    );
    int24 posTickLower = isToken0 ? tailTick : alignTickToTickSpacing(isToken0, TickMath.MIN_TICK, tickSpacing);
    int24 posTickUpper = isToken0 ? alignTickToTickSpacing(isToken0, TickMath.MAX_TICK, tickSpacing) : tailTick;
    require(posTickLower < posTickUpper, InvalidTickRangeMisordered(posTickLower, posTickUpper));
    lpTail = LpPosition({ tickLower: posTickLower, tickUpper: posTickUpper, liquidity: lpTailLiquidity, id: id });
}
```
The UniswapV3Initializer.calculateLpTail() function calculates lpTailLiquidity using MIN_SQRT_PRICE and MAX_SQRT_PRICE, as indicated in lines 281 and 282. However, the lower and upper ticks for minting the lpTail position are not MIN_TICK and MAX_TICK. Instead, they are the aligned ticks determined by the tickSpacing (see lines 287 and 288). Therefore, lpTailLiquidity should be calculated using the sqrt prices corresponding to these aligned ticks, rather than using MIN_SQRT_PRICE and MAX_SQRT_PRICE, which relate to the unaligned ticks MIN_TICK and MAX_TICK. As a result, this discrepancy will create an imbalance between the lower and upper ticks and the liquidity, leading to the minting of an incorrect lpTail position. This, in turn, will cause an imbalance between the bond and sold amounts of the asset during initialization.

Impact Explanation:
High. Minting an incorrect lpTail position may lead to an imbalance between the bond and sold amounts of the asset.

## Recommendation
Avoid using MIN_SQRT_PRICE and MAX_SQRT_PRICE. Instead, utilize the sqrt prices corresponding to the aligned ticks.
