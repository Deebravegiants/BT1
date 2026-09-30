# [M] Function can be called by anyone

## Summary
Severity: Medium
Contest weight: 0.0710
Dataset id: 10700
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the NablaRouter contract, the swapExactTokensForTokens function uses the allowed modifier to check if the caller is allowed to access the function. However, the swapExactTokensForTokensWithoutPriceFeedUpdate function does not have this modifier. As so, any address can bypass the access check in swapExactTokensForTokens by calling PriceOracleAdapter.updatePriceFeeds and swapExactTokensForTokensWithoutPriceFeedUpdate.

## Recommendation
Add the allowed modifier to swapExactTokensForTokensWithoutPriceFeedUpdate.
