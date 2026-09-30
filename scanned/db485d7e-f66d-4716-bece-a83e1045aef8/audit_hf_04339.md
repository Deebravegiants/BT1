# [M] M-14 | liquidityPremium Can Be A Discount

## Summary
Severity: Medium
Contest weight: 0.4391
Dataset id: 21495
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The liquidity premium calculated in function getLiquidityPremium() is calculated as follows: liquidityPremium_ = uint256(uint24(activeTick - BPOOL.floorTick())).divWad(TICK_PREMIUM_FACTOR). If the activeTick is less than TICK_PREMIUM_FACTOR away from the floor tick, then the function returns a proportion less than 100%. Consequently, when the returned proportion is multiplied by the target anchor liquidity in functions sweep() and slide(), the liquidity amount is decreased rather than increased. This results in unexpected liquidity structures when the active tick is less than 4800 ticks from the floor tick. For example, the anchor range liquidity is treated as the "top of book" liquidity, and is targeted to have a basis of 1/1000th of the floor liquidity. However consider a liquidity structure where multiple slides have taken place, and the active tick is 2400 ticks above the floor tick. Now the liquidityPremium is 2400 / 4800 = 0.5, resulting in a targeted anchor liquidity of 1/2000th. The targeted anchor liquidity in this case is less than the configured 1/1000th base ratio, and as the active tick moves closer to the floor tick the targeted anchor liquidity becomes even smaller, which ultimately creates much less price stability when the anchor range is below 4600 ticks in width. Additionally, liquidity is increasingly allocated away from where trading action will accumulate fees when the anchor is collapsing below a width of 4600 ticks.

## Recommendation
When computing the target liquidity threshold for the anchor position, do not allow the anchor position liquidity to drop below the configured 1/1,000th ratio of the floor position liquidity by treating the liquidityPremium as a true premium.
```solidity
uint128 liquidityThreshold = uint128(virtualLiquidityF.mulWad(1e18 + getLiquidityPremium()).divWad(ANCHOR_LIQ_THRESHOLD));
```
