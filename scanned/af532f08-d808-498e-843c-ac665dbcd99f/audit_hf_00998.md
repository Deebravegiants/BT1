# [M] User can spam covers to DoS cover usage

## Summary
Severity: Medium
Contest weight: 0.4264
Dataset id: 3309
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Cover expiry is tracked per tick so that when covers expire the rate, seconds per tick and utilization can be recalculated. Whenever an action happens that involves a change in any of these values these covers need to be tracked. This happens in VirtualPool::_crossingInitializedTick:
```solidity
uint256[] memory coverIds = self.ticks[tick_];
uint256 coveredCapitalToRemove;
uint256 nbCovers = coverIds.length;
for (uint256 i; i < nbCovers; i++) {
    // Add all the size of all covers in the tick
    coveredCapitalToRemove += self.covers[coverIds[i]].coverAmount;
}
```
Here each cover is looped over and its cover amount is added to the total removed which will later be used to update premiumRate, slot0_.secondsPerTick, and utilization. The issue is that a user can open any number of covers for dust amounts and fill up a tick so that this loop can use more gas than is available in a block. Thus causing a denial of service to all interactions involving opening, updating or withdrawing a position or opening/updating or claiming a cover. Hence even though this would be expensive and complicated for the attacker in terms of gas and complicated to perform (as they would need to spread the creation of covers out across multiple blocks), the effect would be a total DoS of the LiquidityManager.

## Recommendation
Consider just tracking the aggregate amounts that are expiring per tick instead of each cover. This would remove the need to loop over the covers and thus the possibility for DoS.
