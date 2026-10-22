# [M] Fee-On-Transfer tokens are not explicitly denied in swap()

## Summary
Severity: Medium
Contest weight: 0.0841
Dataset id: 6804
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The swap() function is used extensively within the Connext protocol, primarily when swapping between local and adopted assets. When a swap is performed, the function will check the actual amount transferred. However, this is not consistent with other swap functions which check that the amount transferred is equal to dx. As a result, overwriting dx with tokenFrom.balanceOf(address(this)).sub(beforeBalance) allows for fee-on-transfer tokens to work as intended.

## Recommendation
Consider adding a require(dx == tokenFrom.balanceOf(address(this)).sub(beforeBalance), "not support fee token"); check prior to overwriting dx to ensure fee-on-transfer tokens are not used in the swap.
