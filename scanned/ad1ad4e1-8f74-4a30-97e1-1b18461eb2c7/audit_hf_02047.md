# [M] Incorrect Amount Of Rewards Used in closePool()

## Summary
Severity: Medium
Contest weight: 0.4602
Dataset id: 11668
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Each pool in the Atlendis protocol follows the defined lifecycle with a number of states: active, defaulted, and closed. While reviewing the current logic to close an active pool, we notice the current implementation needs to be improved. To elaborate, we show below the closePool() routine, which is used to close a current loan. While it properly validates the given loan indicated by its poolHash, it does not compute the right token amount to withdraw from the underlying yield provider. In particular, to facilitate the computation, the protocol normalizes the amount denominated at the 18 decimals, the final withdrawal amount from the underlying yield provider needs to convert back to have the token's decimals. In other words, the current remainingNormalizedLiquidityRewardsReserve (line 368) needs to be in the following form: remainingNormalizedLiquidityRewardsReserve.scaleFromWad(pool.parameters.TOKEN_DECIMALS).
```solidity
function closePool(bytes32 poolHash, address to) external override onlyRole(GOVERNANCE_ROLE) {
    if (poolHash == bytes32(0)) {
        revert Errors.PC_ZERO_POOL();
    }
    if (to == address(0)) {
        revert Errors.PC_ZERO_ADDRESS();
    }
    Types.Pool storage pool = pools[poolHash];
    if (pool.parameters.POOL_HASH != poolHash) {
        revert Errors.PC_POOL_NOT_ACTIVE();
    }
    if (pool.state.closed) {
        revert Errors.PC_POOL_ALREADY_CLOSED();
    }
    pool.state.closed = true;
    uint128 remainingNormalizedLiquidityRewardsReserve = 0;
    if (pool.state.remainingAdjustedLiquidityRewardsReserve > 0) {
        uint128 yieldProviderLiquidityRatio = uint128(pool.parameters.YIELD_PROVIDER.getReserveNormalizedIncome(address(pool.parameters.UNDERLYING_TOKEN)));
        remainingNormalizedLiquidityRewardsReserve = pool.state.remainingAdjustedLiquidityRewardsReserve.wadRayMul(yieldProviderLiquidityRatio);
        pool.state.remainingAdjustedLiquidityRewardsReserve = 0;
    }
    yieldProvider.withdraw(pools[poolHash].parameters.UNDERLYING_TOKEN, remainingNormalizedLiquidityRewardsReserve, to);
    emit PoolClosed(poolHash, remainingNormalizedLiquidityRewardsReserve);
}
```

## Recommendation
Revise the above closePool() logic to compute the right amount to withdraw from the underlying yield provider.
