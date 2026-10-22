# [M] There is no need to assign a bool variable to false as it is the default value this will save a lot of gas

## Summary
Severity: Medium
Reporter: Fluffy Concrete Ram
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
# There is no need to assign a bool variable to false as it is the default value this will save a lot of gas
## Summary
CurveV2FactoryCryptoAdapter.sol line::185

## Vulnerability Detail
Explicitly initializing a variable with it's default value costs unnecessary gas.
There is no need to assign a bool variable to false as it is the default value
this will save a lot of gas

## Impact
high gas use

## Code Snippet
```solidity
CurveV2FactoryCryptoAdapter.sol line::185
bool nonZeroAmountPresent = false;
``` 

## Tool used

Manual Review

## Recommendation
```solidity
bool nonZeroAmountPresent;
```
