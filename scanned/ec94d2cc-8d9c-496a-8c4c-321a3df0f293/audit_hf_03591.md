# [M] YBC-1 | Invalid totalAssets Validation

## Summary
Severity: Medium
Contest weight: 0.0746
Dataset id: 19570
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The getTotalSupply function returns the totalAssets balance rather than the supply of the vault token. However in the BaseCustodian.withdraw function, the shares amount is compared with the result of the getTotalSupply function. Therefore a shares amount is validated being against an underlying token amount.

## Recommendation
In the check in the BaseCustodian on line 79 compare the amount which is a token amount against the result of the getTotalSupply function. Otherwise change the definition of the getTotalSupply function, but be careful to update where it is used, as the validation using the getTotalSupply function in the Portfolio contract is currently correct as it assumes the getTotalSupply is an underlying token amount.
