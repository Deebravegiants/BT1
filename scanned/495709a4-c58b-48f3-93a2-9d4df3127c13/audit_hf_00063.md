# [M] M-02 | Positions Opened Above Max Leverage

## Summary
Severity: Medium
Contest weight: 0.1836
Dataset id: 139
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When validating the creation of a position if the new leverage is over the maxLeverage then the position is adjusted to be at or within the maxLeverage bound. First, the currentLiqPenalty and the liquidationPrice corresponding to maxLeverage is used to select the liquidation tick for the position. Then if the liquidationPenalty is different on the selected tick, that new penalty is applied to the data.liqPriceWithoutPenalty which is ultimately used to determine the leverage of the position. However when the liquidation tick with penalty has a lower liquidationPenalty than the currentLiqPenalty in storage than the resulting liqPriceWithoutPenalty can be higher than the original liqPriceWithoutPenalty which was based on the maxLeverage. maxLeverage = startPrice / (startPrice - liqPriceWithoutPenalty0) Then, since liqPriceWithoutPenalty0 < liqPriceWithoutPenalty1: newLeverage = startPrice / (startPrice - liqPriceWithoutPenalty1) > maxLeverage This is unexpected for the protocol as no positions should have a leverage greater than the maxLeverage. Additionally, it is worth noting that the same can occur for the rebalancer position when determining the liqPriceWithoutPenalty in the _calcRebalancerPositionTick function.

## Recommendation
Consider if it is acceptable to have positions which exceed the maxLeverage. The most straightforward solution would be to configure the maxLeverage accordingly to account for the fact that some positions may go slightly over it depending on the liquidationPenalty updates. Be sure to also keep this in mind when updating the currentLiqPenalty value in storage.
