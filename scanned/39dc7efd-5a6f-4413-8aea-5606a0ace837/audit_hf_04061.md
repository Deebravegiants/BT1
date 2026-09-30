# [M] GMI-1 | GMI Allocations Incorrectly Handle Saturated Markets

## Summary
Severity: Medium
Contest weight: 0.2178
Dataset id: 20513
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a rebalance is underway, the GMI shares to be minted are validated by the _validateMintableAmounts function from the GMI contract.

The function incorrectly considers that the maximum allowed USD equivalent value to be deposited into the asset-specific GMX pool is via the backing token with the lowest availability, not the highest. This results in incorrect asset allocations for cases where the equivalent amount value cannot be deposited in the pool via the saturated backing token, but could have been deposited in the other one.

In _validateMintableAmounts, the maximum ETH value in USD (mintableEth) and maximum USDC value in USD (mintableUsdc) that can be deposited into each GMX asset market per backing token are calculated. Out of these two amounts, the largest should be selected as exactly how much can be deposited into the specific GMX pool using only one operation.

The issue is that the maxMintable chooses the smaller, not the larger out of the 2 values. This results in an incorrect maximum allocation amount for that particular asset pool, lower than it can be deposited. Consider a situation where a GMX pool gets long saturated and the protocol does a rebalance towards the short token.

The _validateMintableAmounts function will incorrectly indicate that the maximum you can deposit into that saturated pool is almost nothing since it uses the lowest available amount from the saturated one for validation.

This situation would result in depositing into the fallback pool, which will revert when also saturated. Ultimately, the protocol becomes imbalanced, risking the loss of user funds.

## Recommendation
Base the previewMint and _validateMintableAmounts functions maximum mint amount on the asset being used to mint, not always take the greater or the smaller one. This would eliminate any issue that may appear due to over or underestimating the maximum amount.
