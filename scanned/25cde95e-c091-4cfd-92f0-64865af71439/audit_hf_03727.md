# [M] PnL is incorrectly counted as collateral when reducing a position

## Summary
Severity: Medium
Contest weight: 0.4441
Dataset id: 19856
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
GMX uses MIN_COLLATERAL_USD to ensure that there is always enough collateral remaining in a position, so that if there are sudden large gaps in prices, there is enough collateral to cover potential losses.

When a position is reduced, the estimate of remaining collateral includes the total P&L as part of the collateral. If a position has a lot of profit, a nefarious owner of the position can reduce the collateral to one wei of the collateral token, and let the position run.

If there is a sudden gap down in price, as is common with crypto Bart price chart formations, the user only loses one wei, but the pool incurs losses because there is no collateral to cover price decreases. Once one wei is left in the position, there is no mechanism for a keeper to reduce the position's leverage, so the only chance thereafter to close the position is when it needs to be liquidated.

PnL is counted as collateral:
```solidity
// File: gmx-synthetics/contracts/position/PositionUtils.sol : PositionUtils.willPositionCollateralBeSufficient()
int256 remainingCollateralUsd = values.positionCollateralAmount.toInt256() * collateralTokenPrice.min.toInt256();

remainingCollateralUsd += values.positionPnlUsd;
if (values.realizedPnlUsd < 0) {
    remainingCollateralUsd = remainingCollateralUsd + values.realizedPnlUsd;
}
if (remainingCollateralUsd < 0) {
    return (false, remainingCollateralUsd);
}
int256 minCollateralUsdForLeverage = Precision.applyFactor(values.positionSizeInUsd, minCollateralFactor).toInt256();
```
cts/position/PositionUtils.sol#L412-L432

The position is only closed if that total is below the minimum collateral dollar amount.

## Recommendation
Do not count PnL as part of the collateral, for the purposes of determining the minimum position collateral amount. The combined value may still be useful as a separate check.
