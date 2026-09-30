# [M] COND-1 | Rounding Down Causes Traders Loss

## Summary
Severity: Medium
Contest weight: 0.0993
Dataset id: 109
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Once a trader sells an option, their balance is expected to be increased by the option’s premium relative to the number of contracts they sold. However, due to the conversion of 18 decimal precision to the precision of the asset, it is possible for a seller to receive no payment for taking on the risk of selling an option. if (assetDecimals < 18) { // Taking the ceil of 10^(18-decimals) will ensure the first n (asset decimals) have precision when converting amount = Math.floor(amount, 10 ** (assetDecimals)); } Any amount below 1 whole unit of an asset will round down to 0, leading to no funds gained on transferCollateral.

## Recommendation
Enforce a minimum amount of contracts to be traded to avoid rounding issues.
