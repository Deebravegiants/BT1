# [M] M-14 | Innacurate isLiquidationPending Check In ValidateOpen

## Summary
Severity: Medium
Contest weight: 0.1535
Dataset id: 171
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The _prepareValidateOpenPositionData function implements the following check:
data_.liqPriceWithoutPenalty = Utils.getEffectivePriceForTick (s, Utils.calcTickWithoutPenalty(data_.action.tick, data_.liquidationPenalty)); data_.lastPrice = s._lastPrice;
if (data_.lastPrice < data_.liqPriceWithoutPenalty) {// the position must be liquidated data_.isLiquidationPending = true; return (data_, false);}
This check compares the s._lastPrice to the liquidation price without the penalty. If the s._lastPrice is lower, the function marks the position as liquidatable and halts further validation. However, this check is not accurate because the liquidation price should factor in the liquidation penalty.
By only comparing against the liquidation price without the penalty, when there is a lastPrice between the liqPriceWithoutPenalty and the actual liquidation price (including the penalty), position is not being flagged for liquidation, even though it should be.

## Recommendation
To fix this, the liquidation check should compare the s._lastPrice against the liquidation price with the penalty. The updated check should look like this:
uint256 liqPrice = Utils.getEffectivePriceForTick(s, data_.posId.tick); if (data_.lastPrice < liqPrice) {// the position must be liquidated data_.isLiquidationPending = true; return (data_, false);}
