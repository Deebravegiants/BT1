# [M] Incorrect Amount Calculation In burnLiquidityShare()

## Summary
Severity: Medium
Contest weight: 0.4532
Dataset id: 13038
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The SorbettoFragola protocol allows users to withdraw their funds from the pool by calling the withdraw() function. The logic behind this implementation is to compute the total liquidity in the position set by the governance at the very beginning. Then, based on the percentage of the share to the total share owned by the user, it further derives the amount of the liquidity that belongs to the user. After this, the protocol removes this part of the liquidity from the pool, and transfers the tokens back to the user. The logic is valid, though there exists a calculation error in this process. In the following, we list below the burnLiquidityShare() function.
```solidity
function burnLiquidityShare(
    IUniswapV3Pool pool,
    int24 tickLower,
    int24 tickUpper,
    uint256 totalSupply,
    uint256 share,
    address to
) internal returns (uint256 amount0, uint256 amount1) {
    require(totalSupply > 0, "TS");
    uint128 liquidityInPool = pool.positionLiquidity(tickLower, tickUpper);
    uint256 liquidity = uint256(liquidityInPool).mul(share) / totalSupply;
    if (liquidity > 0) {
        (amount0, amount1) = pool.burn(tickLower, tickUpper, liquidity.toUint128());
        if (amount0 > 0 || amount1 > 0) {
            // collect liquidity share
            (amount0, amount0) = pool.collect(
                to,
                tickLower,
                tickUpper,
                amount0.toUint128(),
                amount1.toUint128()
            );
        }
    }
}
```
As we can see in the above function, when the contract calls the collect() function from the pool, the outputs are amount0 and amount0 (line 44). The amount0 here represents the amount of token0. However, the purpose of the collect() function is to transfer the exact amount of the token0 and the token1 to the user, so the outputs here should be amount0 and amount1.

## Recommendation
Revise the statement of (amount0, amount0)= pool.collect() to (amount0, amount1)= pool.collect()
