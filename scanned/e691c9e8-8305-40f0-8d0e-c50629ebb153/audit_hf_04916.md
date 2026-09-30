# [M] Estimated prize draws in TieredLiquidityDis-

## Summary
Severity: Medium
Contest weight: 0.1911
Dataset id: 22836
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Estimated prize draws in TieredLiquidityDistributor are off due to rounding down when calculating the expected prize count on each tier, leading to an incorrect next number of tiers and distribution of rewards.
ESTIMATED_PRIZES_PER_DRAW_FOR_5_TIERS and the other tiers are precomputed initially in TieredLiquidityDistributor::_sumTierPrizeCounts(). In here, it goes through all tiers and calculates the expected prize count per draw for each tier. However, when doing this calculation in TierCalculationLib.tierPrizeCountPerDraw(), uint32(uint256(unwrap(sd(int256(prizeCount(_tier))).mul(_odds))));, it rounds down the prize count of each tier. This will lead to an incorrect prize count calculation, for example:
grandPrizePeriodDraws == 8 days
numTiers == 5
prizeCount(tier 0) == 4**0 * 1 / 8 == 1 * 1 / 8 == 0.125 = 0
prizeCount(tier 1) == 4**1 * (1 / 8)^sqrt((1 + 1 - 3) / (1 - 3)) == 4 * 0.2298364718 0.92 = 0
prizeCount(tier 2) == 4**2 * 1 == 16
prizeCount(tier 3) == 4**3 * 1 == 64
total = 80
However, if we multiply the prize counts by a constant and then divide the sum in the end, the total count would be 81 instead, getting an error of 1 / 81 1.12 %
The estimated prize count will be off, which affects the calculation of the next number of tiers in PrizePool::computeNextNumberOfTiers(). This modifies the whole rewards distribution for the next draw.

## Recommendation
Add some precision to the calculations by multiplying, for example, by 1e5 each count and then dividing the sum by 1e5.
uint32(uint256(unwrap(sd(int256(prizeCount(_tier)*1e5)).mul(_odds)))); and return prizeCount / 1e5;.
