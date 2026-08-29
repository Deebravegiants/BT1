# [M] Number of prize tiers may never scale due to aggressive new algorithm

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-08-pooltogether-mitigation
Published: 2023-08-26
Source: https://github.com/code-423n4/2023-08-pooltogether-mitigation-findings/issues/104
Type: code-finding

## Details
# Lines of code

https://github.com/GenerationSoftware/pt-v5-prize-pool/blob/main/src/PrizePool.sol#L369
https://github.com/GenerationSoftware/pt-v5-prize-pool/blob/main/src/PrizePool.sol#L807-L811
https://github.com/GenerationSoftware/pt-v5-prize-pool/blob/main/src/abstract/TieredLiquidityDistributor.sol#L602-L619
https://github.com/GenerationSoftware/pt-v5-prize-pool/blob/main/src/abstract/TieredLiquidityDistributor.sol#L156
https://github.com/GenerationSoftware/pt-v5-prize-pool/blob/main/src/libraries/TierCalculationLib.sol#L134-L147


# Vulnerability details

## Comments
This issue is very similar to M-14 but covers another edge case where the threshold check is not performed when there are currently 14 prize tiers and at least 1 canary tier is claimed. This is due to an early return of `MAXIMUM_NUMBER_OF_TIERS`.

## Mitigation
The updated implementation has significantly changed the tier expansion logic so that it only depends on the total number of prize claims. The current number of tiers and the number of canary tier claims has no impact on the tier expansion logic and therefore the original issue has been resolved. However the updated logic has introduced a new issue.

Note: The same PR fixes multiple issues, but I have arbitrarily chosen to link this new issue with M-16.

## New issue
With the new tier expansion algorithm it is highly likely that the number of prize tiers will stagnate since the percentage of prizes that need to be claimed for a tier expansion increases as the number of tiers increase.

## Proof of Concept
When a draw is closed, the next number of tiers is computed based on the total number of claims with a call to `_computeNextNumberOfTiers`:

```
  function _computeNextNumberOfTiers(uint32 _claimCount) internal view returns (uint8) {
    // claimCount is expected to be the estimated number of claims for the current prize tier.
    uint8 numTiers = _estimateNumberOfTiersUsingPrizeCountPerDraw(_claimCount);
    return numTiers > MAXIMUM_NUMBER_OF_TIERS ? MAXIMUM_NUMBER_OF_TIERS : numTiers; // add new canary tier
  }
```

where the first part of the underlying `_estimateNumberOfTiersUsingPrizeCountPerDraw` method looks like:

```
  function _estimateNumberOfTiersUsingPrizeCountPerDraw(uint32 _prizeCount) internal view returns (uint8) {
    if (_prizeCount < ESTIMATED_PRIZES_PER_DRAW_FOR_4_TIERS) {
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-08-pooltogether-mitigation-findings/issues/104_
