# [H] H-04 | Incorrect Calculation of Upper Tick in Anchor Range

## Summary
Severity: High
Contest weight: 0.5867
Dataset id: 21499
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The MarketMaking policy deploys liquidity to FLOOR, ANCHOR and DISCOVERY positions when rebalancing and their tick boundaries are calculated based on the getTickBoundaries function. The upper tick of ANCHOR (lower tick of DISCOVERY is calculated based on _getUpperAnchorTick which is suppose to return the next highest initialized tick that is a multiple of TICK_SPACING as stated in the docs. Although the _getUpperAnchorTick works with positive ticks, it does not return the correct value for negative ticks. This is due to the fact that the function is rounding the current tick down in absolute value, but negative ticks should be rounded up. When the active tick is in the FLOOR range, the ANCHOR range will disappear when the active tick is positive, but it won't when its negative. This also creates an unexpected scenario where the sweep rebalance operation can be executed when the price is at ANCHOR range. This operation will only check the reserves at ANCHOR, but not the liquidity removed as bAssets, which will be burned.

## Recommendation
Consider refactoring the formula to return the correct value. A suggested approach is:
```solidity
function _getUpperAnchorTick() internal view returns (int24 upperAnchorTick_) {
    if (checkpointTick % TICK_SPACING == 0) return checkpointTick + TICK_SPACING;
    upperAnchorTick_ = (checkpointTick / TICK_SPACING) * TICK_SPACING;
    if (checkpointTick > 0) {
        upperAnchorTick_ += TICK_SPACING;
    }
}
```
