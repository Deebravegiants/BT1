# [M] Protocol fees will make some liquidations un-

## Summary
Severity: Medium
Contest weight: 0.1631
Dataset id: 19774
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When calculating liquidator discount it always uses _minimumCollateralPercentage instead of the the actual collateralization of the debt. If the debt goes too far underwater then the protocol fees will be higher than the actual discount making it unprofitable to liquidate.
ol#L389-L393
When calculating liquidator discount it always uses _minimumCollateralPercentage.
This means that the liquidatorDiscount will be incorrect if the actual ratio is lower than the minimum ratio. Since it takes fees based on liquidatorDiscount it could cost the liquidator more in VOLT than they would receive in collateral.
Example: Assume _minimumCollateralPercentage = 150%. This gives a liquidator discount of 33%. Now imagine that a position being liquidated only has a collateralization of 110%. This gives a liquidator discount of 9%. Since the protocol takes half, it will take 16.33% of the collateral which will make the liquidation unprofitable.
It might seem impossible for the percentage to get low enough to make this an issue but in the event the sequencer goes down liquidations would be delayed.
Liquidations are unprofitable if debt is too far underwater

## Recommendation
Use the actual collateral percentage rather than the minimum to calculate the discount.
