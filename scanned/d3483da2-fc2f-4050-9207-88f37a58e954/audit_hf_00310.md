# [M] `saleRecipient` can rug buyers

## Summary
Severity: Medium
Contest weight: 0.1797
Dataset id: 1540
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In `TokenSaleUpgradeable.sol#buy()`, `tokenIn` will be transferred from the buyer directly to the `saleRecipient` without requiring/locking/releasing the corresponding amount of `tokenOut`.

This allows the `saleRecipient` to rug the users simply by not transferring `tokenOut` and finalizing the sale.

## Proof of Concept
Given:

  * tokenIn: `WBTC`
  * _tokenOutPrice: `1e8`
  * tokenOut: `CTDL`
  * Alice `buy()` with `100e8`;
  * Alice `buy()` with `200e8`;

A malicious `saleRecipient` can just not transfer any `CTDL` to the contract and `finalize()` and keep `300e8 WBTC` received.

As a result, Alice and Bob can not get the expected amount of `tokensOut`, and there is no way to retrieve the WBTC paid, in essence, lose all the funds.

## Recommendation
Instead of transferring the tokenIn directing to the `saleRecipient` in `buy()`, consider transferring the tokenIn into the contract (`address(this)`), and require a sufficient amount of `tokenOut` to be transferred into the contract first before the amount of `tokenIn` can be released to the `saleRecipient`.

**[shuklaayush (BadgerDAO) disagreed with severity](https://github.com/code-423n4/2022-02-badger-citadel-findings/issues/61)**

As this is also an issue regarding abuse of an owner’s admin privileges, it fits the criteria of a `medium` severity issue.

I’ve thought about this more and I’ve decided to split up distinct issues into 3 primary issues:
 
  * Owner rugs users.
  * Funds are transferred to `saleRecipient` before settlement.
  * Changing a token buy price during the sale by front-running buyers by forcing them to purchase at an unfair token price.
 

This issue falls under the second primary issue.
 
  * Funds are transferred to `saleRecipient` before settlement.
