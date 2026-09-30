# [H] BOU-3 | Position Impact Pool Manipulation

## Summary
Severity: High
Contest weight: 0.3604
Dataset id: 18494
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When calculating the PositionPricingUtils.getPriceImpactAmount the difference between the executionPrice
and the latestPrice is used to derive the resulting priceImpactAmount for the positionImpactPool.
However, the executionPrice can be modified to be the acceptablePrice in the event that the acceptablePrice
cannot be fulfilled by the initial max/min latestPrice. This will lead to a difference in the executionPrice and
the latestPrice that is not necessarily from the priceImpactUsd amount.
Example
Consider a LimitIncrease Long order
priceImpactUsd is 0 for simplicity, although this applies when priceImpactUsd is nonzero
The acceptablePrice is not fulfilled by the triggerPrice (max) so the acceptablePrice is used
triggerPrice is used as the _latestPrice in getPriceImpactAmount
However triggerPrice != acceptablePrice (where the acceptablePrice is my executionPrice)
Therefore there is a nonzero priceDiff in getPriceImpactAmount, this is errantly credited as positive PI
and taken out of the impact pool when there is no impact.
As a result, when the acceptablePrice is more favorable than the triggerPrice, the positionImpactPool is
decreased even when the user caused a non-trivial imbalance in the OI and initially had negative
priceImpactUsd.
This will influence the positionImpactPool to trend towards 0 as more orders that have an acceptablePrice
that is more favorable than the triggerPrice are executed. Ultimately this stifles any amount of positive
impact that can be offered to users to balance the OI, since the positive impact amount is capped to the
balance of the positionImpactPool.

## Proof of Concept
https://github.com/GuardianAudits/GMX-4/blob/033061d771f2b327c2fbd4ab59e960109ee85dc2/test/guardian/PoCs.ts#L449

## Recommendation
Consider removing the feature where the user may get their acceptable price if the first price + impact is not
fulfillable and rather revert and have the order canceled/frozen if the acceptablePrice is not met.
Otherwise do not allow users to set an acceptablePrice that is more favorable than the triggerPrice.
