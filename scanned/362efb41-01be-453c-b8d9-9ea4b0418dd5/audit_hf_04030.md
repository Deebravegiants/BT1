# [M] User can prevent liquidations by frontrunning

## Summary
Severity: Medium
Contest weight: 0.2453
Dataset id: 20457
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
User can prevent liquidations by frontrunning the tx and decreasing their debt so that the liquidation transaction reverts.
In the liquidation transaction, the caller has to specify the amount of debt they want to liquidate, _debtAmount. The maximum value for that parameter is the total amount of debt the user holds:
In _calcLiquidation(), the contract determines how much collateral to liquidate when _debtAmount is paid by the caller. In that function, there's a check that reverts if the caller tries to liquidate more than they are allowed to depending on the position's health.
The goal is to get that if-clause to evaluate to true so that the transaction reverts.
To modify your position's health you have two possibilities: either you increase your collateral or decrease your debt. So instead of preventing the liquidation by pushing your position to a healthy state, you only modify it slightly so that the caller's liquidation transaction reverts.
Given that Alice has:
• 100 TAU debt
• 100 Collateral (price = $1 so that collateralization rate is 1) Her position can be liquidated. The max value is:
(1.3e18 * 100e18 - (100e18 * 1e18 * 1e18)/1e18)/1.3e18 = 23.07e18 (leave out liquidation discount for easier math)
The liquidator will probably use the maximum amount they can liquidate and call liquidate() with 23.07e18. Alice frontruns the liquidator's transaction and increases the collateral by 1. That will change the max liquidation amount to:
(1.3e18 * 100e18 - 101e18 * 1e18)/1.3e18 = 22.3e18.
That will cause _calcLiquidation() to revert because 23.07e18 > 22.3e18.
The actual amount of collateral to add or debt to decrease depends on the liquidation transaction. But, generally, you would expect the liquidator to liquidate as much as possible. Thus, you only have to slightly move the position to cause their transaction to revert.
User can prevent liquidations by slightly modifying their position without putting it at a healthy state.

## Recommendation
In _calcLiquidation() the function shouldn't revert if _debtToLiqudiate > _getMaxLiquidation(). Instead, just continue with the value _getMaxLiquidation() returns.
