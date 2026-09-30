# [M] M-15 | Utilization Rate Not Bounded Below 1

## Summary
Severity: Medium
Contest weight: 0.1467
Dataset id: 21115
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The documentation for the getUtilization function states that the collateralUtilization is between zero and one, however this is not true as the lockedCollateralUsd / delegatedCollateralValueUsd ratio is not guaranteed to be below one. While delegated collateral is locked when it’s value drops below the minimumCredit (e.g. lockedCollateralUsd), this does not guarantee that the delegatedCollateralValueUsd will always be greater than the minimumCredit. The delegatedCollateralValueUsd may fall below the minimumCredit based on price action as well as increases in the minimumCredit by the introduction of new positions. As a result the utilization can be above 1e18, which can lead to unexpected utilization fees as well as a DoS when computing the utilization rate with the getCurrentUtilizationRate function. If the utilization rate is allowed to hit > 3e18 then the highUtilizationRateInterest calculation is at risk of overflowing the uint128 and halting all order execution and liquidations in the BFP market.

## Recommendation
Consider explicitly bounding the result from getUtilization below 1e18.
