# [M] Liquidation shouldn't be used to close posi-

## Summary
Severity: Medium
Contest weight: 0.4143
Dataset id: 19835
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
There are various factors associated with minimum collateral requirements, and if a
position falls below them, the position is liquidated.
If the position was over-collateralized and in profit prior to the change in the
minimums, and the minimum is increased, the position is liquidated.
Liquidation gives all funds to the pool, giving nothing back to the user
A position becomes liquidatable once it falls below the changeable collateral
requirements:
```solidity
// File: gmx-synthetics/contracts/position/PositionUtils.sol :
PositionUtils.isPositionLiquidatable()
    if (shouldValidateMinCollateralUsd) {
        cache.minCollateralUsd =
            dataStore.getUint(Keys.MIN_COLLATERAL_USD).toInt256();
        if (cache.remainingCollateralUsd < cache.minCollateralUsd) {
            return true;
        }
    }
    if (cache.remainingCollateralUsd <= 0) {
        return true;
    }
    // validate if (remaining collateral) / position.size is less
    than the min collateral factor (max leverage exceeded)
```
Liquidations give everything to the pool, and nothing to the position's account

## Recommendation
Close the position with a market order, rather than liquidating it, if the user was
previously above the minimum with the old factor
