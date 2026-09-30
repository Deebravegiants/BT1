# [C] C-05 | Wrong Collateral Discount

## Summary
Severity: Critical
Contest weight: 0.1541
Dataset id: 22076
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The discounted collateral is computed in valueInUsd. A discount is a value between lowerLimitDiscount and upperLimitDiscount that depends on the impact on the spot market. The calculation is wrong as it has reversed the places of the min and max functions, which will result in wrong calculation. The discount will always be computed using the upperLimitDiscount, no matter the impact on the market. In result, the users' total collateral value will be less than it has to be, which can lead to earlier liquidations.

## Recommendation
Switch the ordering of the min and max functions.
