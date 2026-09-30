# [H] Velodrome staked position are significantly

## Summary
Severity: High
Contest weight: 0.7844
Dataset id: 22938
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Velodrome staked position are significantly overvalued Let's see how Velodrome LP positions are valued within VelodromeCLAssetGuard
```solidity
(uint256 amount0, uint256 amount1) = nonfungiblePositionManager.total(tokenId, poolParams.sqrtPriceX96);
tokenBalance = tokenBalance.add(_assetValue(pool, poolParams.token0, amount0)).add(
    _assetValue(pool, poolParams.token1, amount1)
);
```
```solidity
function total(
    IVelodromeNonfungiblePositionManager positionManager,
    uint256 tokenId,
    uint160 sqrtRatioX96
) internal view returns (uint256 amount0, uint256 amount1) {
    (uint256 amount0Principal, uint256 amount1Principal) = principal(positionManager, tokenId, sqrtRatioX96);
    (uint256 amount0Fee, uint256 amount1Fee) = fees(positionManager, tokenId);
    return (amount0Principal + amount0Fee, amount1Principal + amount1Fee);
}
```
```solidity
function _fees(
    IVelodromeNonfungiblePositionManager positionManager,
    FeeParams memory feeParams
) private view returns (uint256 amount0, uint256 amount1) {
    (uint256 poolFeeGrowthInside0LastX128, uint256 poolFeeGrowthInside1LastX128) = _getFeeGrowthInside(
        IVelodromeCLPool(
            PoolAddress.computeAddress(
                positionManager.factory(),
                PoolAddress.PoolKey({token0: feeParams.token0, token1: feeParams.token1, tickSpacing: feeParams.tickSpacing})
            )
        ),
        feeParams.tickLower,
        feeParams.tickUpper
    );
    amount0 = FullMath.mulDiv(
        poolFeeGrowthInside0LastX128 - feeParams.positionFeeGrowthInside0LastX128,
        feeParams.liquidity,
    ) + feeParams.tokensOwed0;
    amount1 = FullMath.mulDiv(
        poolFeeGrowthInside1LastX128 - feeParams.positionFeeGrowthInside1LastX128,
        feeParams.liquidity,
    ) + feeParams.tokensOwed1;
}
```
The problem is that fees are calculated based on the last value of position's positionFeeGrowthInside1LastX128 (what fees the position would usually have earned if it hadn't been staked). However, staked Velodrome positions actually do not accrue any pool fees. They only earn gauge rewards. Consider a LP position for $1000 worth of tokens:
• if it was not staked it would've earned $500 in fees.
• since it is staked, it has earned $1000 in gauge rewards Although the LP position is worth $2000, the current implementation of the code would value it at $2500. The longer the LP positions has been active, the bigger discrepancy there will be. This would cause users to deposit based on an inflated value of the Pool. Upon adjustment of the LP position (to sync it with the Velodrome Pool), this would result in an instant loss for the new depositors. Wrong valuation of LP positions.

## Recommendation
Do not calculate fees if position is staked
