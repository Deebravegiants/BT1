# [M] No slippage protection

## Summary
Severity: Medium
Contest weight: 0.3972
Dataset id: 4198
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Burve contract allows users to provide liquidity to both the Island pool and Uniswap V3 pools. The number of shares minted to users is determined using the following calculation:
```solidity
function islandLiqToShares(uint128 liq) internal view returns (uint256 shares) {
    if (address(island) == address(0x0)) {
        revert NoIsland();
    }
    (uint160 sqrtRatioX96,,,,,,) = pool.slot0();
    (uint256 amount0, uint256 amount1) = getAmountsFromLiquidity(
        sqrtRatioX96,
        island.lowerTick(),
        island.upperTick(),
        liq
    );
    (,, shares) = island.getMintAmounts(amount0, amount1);
}
```
Since the amount of shares depends on sqrtRatioX96, any fluctuations in this value will impact the number of shares users receive. As a result, users may end up with fewer tokens than expected.

## Recommendation
Consider adding a minSharesOut parameter to the mint/burn functions.
