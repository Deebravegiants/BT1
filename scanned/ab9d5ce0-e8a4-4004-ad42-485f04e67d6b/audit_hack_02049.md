# [M] 6.2 Incorrect Conversion to 18 Decimals

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Correctness Medium Version 1 Code Corrected

An additional call to convertTo18() has been added compared to the codebase from the previous
report.

In _closeWithdrawCollateralSkipFL(), the following code is executed:

```
cdpData.withdrawCollateral = convertTo18(cdpData.gemJoin, cdpData.withdrawCollateral);
```
```
wipeAndFreeGem(
addressRegistry.manager,
cdpData.gemJoin,
```

```
cdpData.cdpId,
cdpData.requiredDebt,
cdpData.withdrawCollateral
);
```
wipeAndFreeGem() contains the following code where collateralDraw is equal to
cdpData.withdrawCollateral:

```
uint256 wadC = convertTo18(cdpData.gemJoin, collateralDraw);
```
Thus, wadC will be
withdrawCollateral*10**(18-gem.decimals())*10**(18-gem.decimals()). Ultimately,
that results in an incorrect amount.

Code corrected:

The conversion to 18 decimals has been removed in _closeWithdrawCollateralSkipFL().
