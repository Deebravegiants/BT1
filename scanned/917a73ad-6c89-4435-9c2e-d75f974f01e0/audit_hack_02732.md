# [H] Decimal conversion in OptionMath.sol

## Summary
Severity: High
Reporter: __141345__
Source: https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/libraries/OptionMath.sol#L158-L170
Type: audit-issue

## Details
# Decimal conversion in OptionMath.sol

## Summary

The calculation for potential total contracts is using the `fromContractsToCollateral()`. But the decimal calculation is not correct, which could lead to wrong total contracts results, and over sell options. Potentially lead to vault insolvency.



## Vulnerability Detail

But the decimal conversion does not consider both the `baseDecimals` and `underlyingDecimals`.

## Impact

`_getTotalContracts()` will return inaccurate results. The vault could over sell options, in some cases lead to insolvency.



## Code Snippet

https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/libraries/OptionMath.sol#L158-L170


## Tool used

Manual Review


## Recommendation

Change to:
```solidity
        int128 collateral64x64 = collateral.fromDecimals(baseDecimals);
        return collateral64x64.div(strike64x64).toDecimals(underlyingDecimals);
```
