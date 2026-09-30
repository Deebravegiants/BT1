# [M] M-19 | Inaccurate aumUsd When Removing Liquidity

## Summary
Severity: Medium
Contest weight: 0.1275
Dataset id: 2120
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When removing liquidity from the collateral pool, a check is performed to ensure that the remaining asset value is sufficient to cover the reservedUsd amount. This check is implemented using require(reservedUsd = aumUsd). This aumUsd value being compared to reservedUsd is calculated by subtracting the value of the removed asset from the pool’s previous aumUsd value: aumUsd = removedValue. However, after this calculation, a portion of the removedValue is deposited back into the pool during _distributeFee. Normally, this deposited amount increases the pool’s aumUsd. However, this increase is not accounted for, making the aumUsd value used in the require(reservedUsd = aumUsd) statement inaccurate. As a result, liquidity removal may fail incorrectly with an InsufficientLiquidity error, even though the actual aumUsd is sufficient to cover reservedUsd.

## Recommendation
Re-added fees should be accounted for during the calculation.
