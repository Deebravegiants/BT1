# [H] H-09 | Deleverage Can Break Through Floor Tick

## Summary
Severity: High
Contest weight: 0.1295
Dataset id: 21462
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When deleveraging an account, the floor tick can be breached because the account’s borrowed reserves have not yet been added to the floor tick, therefore the capacity cannot handle the flash swap — which assumes there is enough liquidity to sell the bAsset collateral before the borrowed reserves have been re-added.

## Recommendation
Consider adding a requirement to the deleverage function that the existing liquidity structure, not including the virtual floor liquidity, can comfortably handle the sell of the bAsset collateral.
Otherwise remove the deleverage feature and require users to deleverage manually, or implement a periphery contract which performs naive deleverages, without flash swapping, on behalf of the user.
