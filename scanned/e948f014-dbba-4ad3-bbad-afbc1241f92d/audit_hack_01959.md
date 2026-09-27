# [M] 6.1 Unadapted amountToLiquidate

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design Medium Version 1 Code Corrected

In liquidateLogic, amountToLiquidate is computed before amountToSeize is capped. However,
amountToLiquidate is not adapted to the capped amountToSeize, which may cause the liquidator to
repay more than the value of the collateral they obtain.

Code corrected:

If amountToSeize exceeds the amount of the liquidated user's collateral balance of the requested
token, amountToLiquidate is adjusted as follows:


```
amountToLiquidate = ((collateralBalance * collateralPrice * vars.borrowedTokenUnit) /
(borrowedTokenPrice * vars.collateralTokenUnit))
.percentDiv(vars.liquidationBonus);
```
