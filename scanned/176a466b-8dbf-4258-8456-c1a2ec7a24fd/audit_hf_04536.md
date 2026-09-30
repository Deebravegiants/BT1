# [M] M-17 | Max Collateral Can Be Exceeded Through payDebt

## Summary
Severity: Medium
Contest weight: 0.1118
Dataset id: 22100
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the modifyCollateral function, the added collateral amount is validated through
globalPerpsMarket.validateCollateralAmount to ensure that the maximum collateral limit is not
exceeded.
However, in the payDebt function, this check is not performed, even though the function can increase
an account's sUSD collateral (as any excess over the amount used to pay debt is added to the
collateral).
Additionally, sUSD collateral may exceed the maximum amount through the realization of profits.
Moreover, the payDebt function lacks the validation to ensure that the maximum number of collateral
types per account is not exceeded, which is done through PerpsAccount.validateMaxCollaterals.

## Recommendation
In the payDebt function, call: globalPerpsMarket.validateCollateralAmount and
PerpsAccount.validateMaxCollaterals to ensure both max collateral amount and types are not
exceeded.
