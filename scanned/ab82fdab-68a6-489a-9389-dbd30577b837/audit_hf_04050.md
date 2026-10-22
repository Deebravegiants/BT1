# [M] fee calculations

## Summary
Severity: Medium
Contest weight: 0.3905
Dataset id: 20489
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
in/concentrator/contracts/Multipool.sol#L722-L746, these LOCs don't allow underflow/overflow, but refering to https://github.com/Uniswap/v3-core/issues/573 which allows underflow/overflow. This will lead to some transactions will revert. • some user transactions will revert. ```solidity if (liquidity > 0) { ( uint256 feeGrowthInside0X128Pending, uint256 feeGrowthInside1X128Pending ) = _getFeeGrowthInside( IUniswapV3Pool(position.poolAddress), slots[i].tick, position.lowerTick, position.upperTick ); pendingFee0 += uint128( FullMath.mulDiv( feeGrowthInside0X128Pending - feeGrowthInside0LastX128, liquidity, ) ); pendingFee1 += uint128( FullMath.mulDiv( feeGrowthInside1X128Pending - feeGrowthInside1LastX128, liquidity, ) ); } ```

## Recommendation
add unchecked {} when calculate the pending fee
