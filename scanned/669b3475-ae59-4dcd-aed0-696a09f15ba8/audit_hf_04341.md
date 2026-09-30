# [H] H-02 | Invalid Leverage Factor Calculation

## Summary
Severity: High
Contest weight: 0.2077
Dataset id: 21497
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The leverage factor is calculated as the ratio between the totalCollateralized and the spot supply (externally owned bAssets). Whenever sweep or slide rebalances are executed, the leverage factor will act as a multiplier for the liquidityPremium. The main issue relies on the calculation of this multiplier. The first part of the formula correctly calculates the ratio: leverageFactor_ = totalCollateral / (_bAssetsCirculating - totalCollateral); But the value returned by the function is: leverageFactor_ += 1e18; This means that if the ratio is 5, the leverage factor will be 1e18 + 5 instead of 5e18 or a 5x multiplier. The issue can also be found at [InitializeProtocol.sol#L166](https://github.com/GuardianAudits/baseline-team-1-pocs/blob/main/src/policies/InitializeProtocol.sol#L166) as well.

## Recommendation
Use the FixedPointMathLib lib to correctly return the multiplier value: leverageFactor_ = 1e18 + totalCollateral.divWad(_bAssetsCirculating - totalCollateral);
