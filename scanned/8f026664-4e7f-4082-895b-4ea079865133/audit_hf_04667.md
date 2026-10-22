# [M] Low precision is used when checking spot

## Summary
Severity: Medium
Contest weight: 0.6864
Dataset id: 22412
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Low precision is used when checking spot price deviation, which might lead to potential manipulation or create the potential for an MEV opportunity due to valuation discrepancy. Assume the following:
• The max deviation is set to 1%
• nTokenOracleValue is 1,000,000,000
• nTokenSpotValue is 980,000,001
File: Constants.sol
46:
```solidity
// Basis for percentages
47:
int256 internal constant PERCENTAGE_DECIMALS = 100;
```
File: nTokenCalculations.sol
61:
```solidity
int256 maxValueDeviationPercent = int256(
    uint256(uint8(nToken.parameters[Constants.MAX_MINT_DEVIATION_LIMIT]))
);
// Check deviation limit here
int256 deviationInPercentage = nTokenOracleValue.sub(nTokenSpotValue).abs()
    .mul(Constants.PERCENTAGE_DECIMALS).div(nTokenOracleValue);
require(deviationInPercentage <= maxValueDeviationPercent, "Over Deviation Limit");
```
Based on the above formula:
```solidity
nTokenOracleValue.sub(nTokenSpotValue).abs().mul(Constants.PERCENTAGE_DECIMALS).div(nTokenOracleValue);
```
((nTokenOracleValue - nTokenSpotValue) * Constants.PERCENTAGE_DECIMALS) / nTokenOracleValue
((1,000,000,000 - 980,000,001) * 100) / 1,000,000,000
(19,999,999 * 100) / 1,000,000,000 = 1,999,999,900 / 1,000,000,000 = 1.9999999 = 1
The above shows that the oracle and spot values have deviated by 1.99999%, which is close to 2%. However, due to a rounding error, it is rounded down to 1%, and the TX will not revert. The purpose of the deviation check is to ensure that the spot market value is not manipulated. If the deviation check is not accurate, it might lead to potential manipulation or create the potential for an MEV opportunity due to valuation discrepancy.

## Recommendation
Consider increasing the precision. For instance, increasing the precision from Constants.PERCENTAGE_DECIMALS (100) to 1e8 will prevent rounding down.
```solidity
nTokenOracleValue.sub(nTokenSpotValue).abs().mul(1e8).div(nTokenOracleValue);
((nTokenOracleValue - nTokenSpotValue) * 1e8) / nTokenOracleValue
((1,000,000,000 - 980,000,001) * 1e8) / 1,000,000,000 = 1999999.9 = 1999999
1% of 1e8 = 1000000
require(deviationInPercentage <= maxValueDeviationPercent, "Over Deviation Limit")
require(1999999 <= 1000000, "Over Deviation Limit") => Revert
```
