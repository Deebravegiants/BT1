# [H] H-05 | DoS Via validateMinimumCredit

## Summary
Severity: High
Contest weight: 0.1887
Dataset id: 2275
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the validateMinimumCredit function the delegatedCollateralValueUsd is compared to the minimumCredit, however the minimumCredit for the PerpMarket includes the market sUSD collateral as this amount is included in the creditCapacity which is ultimately validated against the minimumCredit. Therefore the delegatedCollateralValueUsd cannot directly be compared against the market’s minimumCredit, as the delegatedCollateralValueUsd does not include the trader deposited sUSD amount. One can deposit big chunks of sUsd as a collateral from BFP side via modifyCollateral such that all position increase orders will fail. It can also happen naturally without requiring a malicious intent because of wrong accounting.

## Recommendation
Update the validation to delegatedCollateralValueUsd + market.depositedCollateral[SYNTHETIX_SUSD] < minimumCredit.toInt().
