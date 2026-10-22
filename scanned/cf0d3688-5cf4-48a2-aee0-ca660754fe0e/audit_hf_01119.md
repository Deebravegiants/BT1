# [H] Incorrect tick calculation leads to DoS

## Summary
Severity: High
Reporter: etherhood
Contest weight: 1.0000
Dataset id: 4590
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Assuming isToken0 is true. In Doppler, in rebalance function, currentTick is calculated as follows:
```solidity
currentTick =
_alignComputedTickWithTickSpacing(adjustmentTick + (accumulatorDelta / I_WAD).toInt24(), key.tickSpacing);
```
and to calculate tickLower and tickUpper:
```solidity
(int24 tickLower, int24 tickUpper) = _getTicksBasedOnState(newAccumulator, key.tickSpacing);
```
This might look okay, but there is an issue in this construction, accumulatorDelta is much smaller than newAccumulator which is sum of all accumulatorDelta calculated in previous calls. This results in currentTick being higher than tickLower. In lowerSlug, tickLower is upperTick and currentTick is lowerTick, this inconsistency cause an error while doing modifyLiquidity call for updating the LP positions, thus not allowing anymore swaps by its construction, till sale period ends in which users can sell assets back for numeraire token.

## Proof of Concept
This test fails for next swap because of the above issue, this fails during swap 3.
```solidity
function test_doppler_dos() public {
    uint256 numPDSlugs = hook.getNumPDSlugs();
    uint256 timeDelta = hook.getEndingTime() - hook.getStartingTime();
    vm.warp(hook.getStartingTime());
    buyExactIn(hook.getMinimumProceeds()/5);
    console2.log("Swap 1");
    vm.roll(block.number + 1);
    vm.warp(hook.getStartingTime() + timeDelta/5);
    buyExactIn(hook.getMinimumProceeds()*2/5);
    vm.roll(block.number + 1);
    vm.warp(hook.getStartingTime() + timeDelta*2/5);
    console2.log("Swap 2");
    buyExactIn(hook.getMinimumProceeds());
    vm.roll(block.number + 1);
    vm.warp(hook.getStartingTime() + timeDelta*3/5);
    console2.log("Swap 3");
}
```
Here is the log of ticks for each slug.
----------------
Lower Slug
tickLower -67128
tickUpper -67136
----------------
Upper Slug
tickLower -67136
tickUpper -67128
----------------
PD Slug
tickLower -67128
tickUpper -66864
----------------
PD Slug
tickLower -66864
tickUpper -66600
----------------
PD Slug
tickLower -66600
tickUpper -66336
It is clear ticks in Lower Slug are inconsistent as compared to others.

## Recommendation
The solution is not clear, root cause lies in either _getMaxTickDeltaPerEpoch:
```solidity
return int256(endingTick - effectiveStartingTick) * I_WAD / int256((endingTime - startingTime) / epochLength);
```
Because it keeps on returning increasing values of accumulatorDelta, which is accumulated in newAccumulate, or in:
```solidity
currentTick =
_alignComputedTickWithTickSpacing(adjustmentTick + (accumulatorDelta / I_WAD).toInt24(), key.tickSpacing);
(int24 tickLower, int24 tickUpper) = _getTicksBasedOnState(newAccumulator, key.tickSpacing);
```
Which is then used in calculation of tickLower, unlike currentTick which only use accumularDelta. Thus reducing tickLower more than currentTick.
