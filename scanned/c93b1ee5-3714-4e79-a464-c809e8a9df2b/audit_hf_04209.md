# [M] M-02 | Full Utilization DoS

## Summary
Severity: Medium
Contest weight: 0.0915
Dataset id: 21102
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When computing the current utilization in the PerpMarket.getUtilization function if the backing
liquidity is over-utilized, e.g. delegatedCollateralValueUsd < 0, then a utilization of 100% is returned.
However when the backing liquidity is exactly 100% utilized, e.g. delegatedCollateralValueUsd == 0
then the function will attempt to divide the lockedCollateralUsd by the delegatedCollateralValueUsd,
resulting in a divide by 0 panic revert.
However, the risk of DoS is unlikely as the utilization is unlikely to be able to get to exactly 100%.

## Recommendation
Modify the if condition on line 191 such that the PerpMarket.getUtilization function early returns if
delegatedCollateralValueUsd <= 0.
