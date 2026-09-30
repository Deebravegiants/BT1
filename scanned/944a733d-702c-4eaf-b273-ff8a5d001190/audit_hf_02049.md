# [M] Improved yieldProviderLiquidityRatio Update in BorrowerPools

## Summary
Severity: Medium
Contest weight: 0.4599
Dataset id: 11675
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Atlendis protocol provides certain ways to incentivize liquidity providers to provide liquidity on Atlendis. First of all, the idle capital is placed on Aave, where the earned interest is integrated into the liquidity provider's position on the Atlendis protocol, enabling them to increase their exposure and earn additional interest. Moreover, Liquidity providers can accumulate liquidity rewards paid by the borrower once their funds have been exposed to being borrowed. Both the Aave interest and the liquidity rewards can be accumulated manually or automatically via the collectFees() routine. While examining the logic to accumulate fees, we notice the existence of improper update of the pool.state.yieldProviderLiquidityRatio, which impacts the fees collection for the following ticks. To elaborate, we show below code snippets from the PoolLogic library. As the name indicates, the collectFees() routine is designed for a user to collect fees for the given tick in the pool. It will call the collectFeesForTick() routine which will further invoke the peekFeesForTick() routine to peek the updated liquidity ratio and accrued fees for the target tick. The peekFeesForTick() routine calculates the yield liquidity ratio increase via yieldProviderLiquidityRatio - pool.state.yieldProviderLiquidityRatio (line 563), where the yieldProviderLiquidityRatio is the latest yield liquidity ratio read from Aave and the pool.state.yieldProviderLiquidityRatio is the yield liquidity ratio recorded when the last time the collectFees() routine is invoked. It comes to our attention that the pool.state.yieldProviderLiquidityRatio is updated every time when the collectFees() is invoked, even the pool has available funds on several ticks. As a result, collecting fees for one tick will impact the fees collection for the following ticks as the pool.state.yieldProviderLiquidityRatio has been updated to the latest.
```solidity
function collectFees(Types.Pool storage pool, uint128 rate) internal {
    uint128 yieldProviderLiquidityRatio = uint128(pool.parameters.YIELD_PROVIDER.getReserveNormalizedIncome(address(pool.parameters.UNDERLYING_TOKEN)));
    pool.collectFeesForTick(rate, yieldProviderLiquidityRatio);
    pool.state.yieldProviderLiquidityRatio = yieldProviderLiquidityRatio;
}

function peekFeesForTick(Types.Pool storage pool, uint128 rate, uint128 yieldProviderLiquidityRatio) internal view returns (uint128 updatedAtlendisLiquidityRatio, uint128 updatedAccruedFees, uint128 liquidityRewardsIncrease) {
    Types.Tick storage tick = pool.ticks[rate];
    if (tick.atlendisLiquidityRatio == 0) {
        return (yieldProviderLiquidityRatio, 0, 0);
    }
    updatedAtlendisLiquidityRatio = tick.atlendisLiquidityRatio;
    updatedAccruedFees = tick.accruedFees;
    uint128 yieldProviderLiquidityRatioIncrease = yieldProviderLiquidityRatio - pool.state.yieldProviderLiquidityRatio;
    // get additional fees from liquidity rewards
    liquidityRewardsIncrease = pool.getLiquidityRewardsIncrease(rate);
    uint128 currentNormalizedRemainingLiquidityRewards = pool.state.remainingAdjustedLiquidityRewardsReserve.wadRayMul(yieldProviderLiquidityRatio);
    if (liquidityRewardsIncrease > currentNormalizedRemainingLiquidityRewards) {
        liquidityRewardsIncrease = currentNormalizedRemainingLiquidityRewards;
    }
    // if no ongoing loan, all deposited amount gets the yield provider and liquidity rewards so the global liquidity ratio is updated
    if (pool.state.currentMaturity == 0) {
        updatedAtlendisLiquidityRatio += yieldProviderLiquidityRatioIncrease;
    }
    if (tick.adjustedRemainingAmount > 0) {
        updatedAtlendisLiquidityRatio += liquidityRewardsIncrease.wadToRay().wadDiv(tick.adjustedRemainingAmount);
    }
    // if ongoing loan, accruing fees components are added, liquidity ratio will be updated at repay time
    else {
        updatedAccruedFees += tick.adjustedRemainingAmount.wadRayMul(yieldProviderLiquidityRatioIncrease);
    }
}
```

## Recommendation
Revise the above collectFees() logic to record the yieldProviderLiquidityRatio per tick properly.
