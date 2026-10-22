# [H] Cover premium rewards can be lost

## Summary
Severity: High
Contest weight: 0.5884
Dataset id: 3324
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Premiums paid by the cover holders are periodically distributed to the liquidity providers. This is done on all calls affecting the pool utilization. It goes down to a function VirtualPool::_refreshSlot0 which has all the logic for updating the current tick and new utilization and updating the cover premium rewards. The way it works is that it calculates the current tick and then checks which covers are expiring between the last tick checked and the new current tick:
```solidity
if (isInitialized) {
    (slot0, utilization, premiumRate) = self._crossingInitializedTick(slot0, nextTick);
}
// Remove parsed tick size from remaining time to current timestamp
remaining -= secondsToNextTickEnd;
secondsParsed = secondsToNextTickEnd;
slot0.tick = nextTick + 1;
} else {
}

slot0.liquidityIndex += PoolMath.computeLiquidityIndex(
    utilization,
    premiumRate,
    secondsParsed
);
```
The issue is that the liquidity index is computed with the new utilization and premium rate. Hence any last rewards from the closed cover will be lost. The most extreme case would be a cover that's opened and closed between when _refreshSlot0 is called, then all the premiums from that position would be lost.

## Recommendation
Consider calculating the liquidity index before crossing an initialized tick as well.
