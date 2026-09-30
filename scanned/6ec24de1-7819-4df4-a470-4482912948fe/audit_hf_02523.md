# [M] Typo in price1 calculation.

## Summary
Severity: Medium
Contest weight: 0.0535
Dataset id: 13475
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
`price1` calculation used `stable0` value instead of `stable1`. It will cause `pairFor` function to return wrong address and most likely cause a revert. In extreme scenario it could return wrong price. <https://github.com/Canto-Network/lending-updates/blob/8f1e624a74ea67e63400209dded2bb716d92e472/src/Swap/BaseV1-periphery.sol#L539>

## Recommendation
No recommendation
