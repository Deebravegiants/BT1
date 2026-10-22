# [M] M-26 | Oracle Incompatible With Non-Standard Tokens

## Summary
Severity: Medium
Contest weight: 0.0633
Dataset id: 22197
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The current logic in getPrices will underflow when the BASE token has more than 18 decimals: uint256 _priceOne18 = _priceBaseSpTKN * 10 ** (18 - IERC20Metadata(BASE_TOKEN).decimals()); This will entirely prevent oracle compatibility with borrow tokens that have more than 18 decimal precision, which is problematic in Peapods which is a permissionless system.

## Recommendation
Query the decimals first and if it is greater than 18, subtract 18 from the base token’s decimals.
