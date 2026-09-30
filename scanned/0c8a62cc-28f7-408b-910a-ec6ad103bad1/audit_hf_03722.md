# [M] Virtual impacts can be trivially bypassed via multiple small orders

## Summary
Severity: Medium
Contest weight: 0.4411
Dataset id: 19846
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Virtual impacts can be trivially bypassed by chopping large orders into multiple smaller ones. Virtual price impacts are meant to ensure that even if a user spreads their orders over multiple pools, that they still will have a sufficient price impact to deter oracle price manipulation. The code, however, allows smaller orders to go through without incurring this global virtual price impact.

A user can get around a large virtual price impact by chopping their large orders into multiple smaller orders, below the price impact threshold, manipulate the oracle price, and have all of the small orders executed in the same block, defeating the manipulation protection.

Only looks at change in position:
```solidity
// File: gmx-synthetics/contracts/pricing/PositionPricingUtils.sol : PositionPricingUtils.getPriceImpactUsd()
if (!hasVirtualInventory) {
    return priceImpactUsd;
}
OpenInterestParams memory openInterestParamsForVirtualInventory = getNextOpenInterestForVirtualInventory(params);

int256 priceImpactUsdForVirtualInventory = _getPriceImpactUsd(params.dataStore, params.market, openInterestParamsForVirtualInventory);

int256 thresholdPriceImpactUsd = Precision.applyFactor(params.usdDelta.abs(), thresholdImpactFactorForVirtualInventory);

if (priceImpactUsdForVirtualInventory > thresholdPriceImpactUsd) {
    return priceImpactUsd;
}
return priceImpactUsdForVirtualInventory < priceImpactUsd ? priceImpactUsdForVirtualInventory : priceImpactUsd;
}
```
cts/pricing/PositionPricingUtils.sol#L207-L222

## Recommendation
Virtual price impact needs to always apply, in order to solve for the case of splitting a large order over multiple accounts. If orders split over multiple accounts is not a risk you want to address, the price impact should at least take into account the total position size for a single account when determining whether the threshold should apply.
