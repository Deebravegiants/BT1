# [M] M-03 | previewAddLiquidity Disagrees With _adjustLiquidity

## Summary
Severity: Medium
Contest weight: 0.1136
Dataset id: 20856
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the _adjustAddLiquidity function the baseAdjustedInAmount and quoteAdjustedInAmount are adjusted without considering tokens that may be sitting in the MagicLP contract and unaccounted for in the reserves. Therefore the result from _adjustAddLiquidity contradicts the result retrieved from previewAddLiquidity when there are excess tokens sitting in the MagicLP contract as the previewAddLiquidity function accounts for the current token balance of the lp contract. As a result in some cases the resulting baseAdjustedInAmount and quoteAdjustedInAmount users would expect to pay using the previewAddLiquidity function will not line up with the baseAdjustedInAmount and quoteAdjustedInAmount that are paid in actuality.

## Recommendation
Consider accounting for any additional tokens in the lp contract to match the behavior of the previewAddLiquidity function.
