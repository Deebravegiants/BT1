# [H] initialCollateralDeltaAmount is incorrectly in-

## Summary
Severity: High
Contest weight: 0.6340
Dataset id: 20039
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Decrease orders have checks to ensure that if collateral is withdrawn, that there is enough left that the liquidation checks will still pass. The code that calculates the remaining collateral incorrectly adds a token amount to a USD value. initialCollateralDeltaAmount is incorrectly interpreted as a USD value when calculating estimated remaining collateral which means, depending on the token's decimals, the collateral will either be accepted or not accepted, when it shouldn't be. If the remaining collateral is over-estimated, the MIN_COLLATERAL_USD checks later in the function will pass, and the user will be able decrease their collateral, but then will immediately be liquidatable by liquidation keepers, since liquidation orders don't attempt to change the collateral amount. If the remaining collateral is under-estimated, the user will be incorrectly locked into their position. initialCollateralDeltaAmount() isn't converted to a USD amount before being added to estimatedRemainingCollateralUsd, which is a USD amount:
```solidity
// File: gmx-synthetics/contracts/position/DecreasePositionUtils.sol : DecreasePositionUtils.decreasePosition()
// the estimatedRemainingCollateralUsd subtracts the initialCollateralDeltaAmount
// since the initialCollateralDeltaAmount will be set to zero, the initialCollateralDeltaAmount
// should be added back to the estimatedRemainingCollateralUsd
estimatedRemainingCollateralUsd += params.order.initialCollateralDeltaAmount().toInt256();
params.order.setInitialCollateralDeltaAmount(0);
}
// if the remaining collateral including position pnl will be below
// the min collateral usd value, then close the position
// if the position has sufficient remaining collateral including pnl
// then allow the position to be partially closed and the updated
// position to remain open
if ((estimatedRemainingCollateralUsd + cache.estimatedRemainingPnlUsd) < params.contracts.dataStore.getUint(Keys.MIN_COLLATERAL_USD).toInt256()) {
```
gmx-synthetics/contracts/position/DecreasePositionUtils.sol#L132-L152

## Recommendation
Convert to a USD amount before doing the addition
