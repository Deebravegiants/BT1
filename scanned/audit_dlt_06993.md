# [M] [WP-H3] `saleRecipient` can rug buyers

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-02-badger-citadel
Published: 2022-02-06
Source: https://github.com/code-423n4/2022-02-badger-citadel-findings/issues/61
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2022-02-badger-citadel/blob/main/contracts/TokenSaleUpgradeable.sol#L180-L183


# Vulnerability details

In `TokenSaleUpgradeable.sol#buy()`, `tokenIn` will be transferred from the buyer directly to the `saleRecipient` without requiring/locking/releasing the correspoining amount of `tokenOut`.

This allows the `saleRecipient` to rug the users simply by not transferring `tokenOut` and finalizing the sale.

### PoC

Given:

- tokenIn: `WBTC`
- _tokenOutPrice: `1e8`
- tokenOut: `CTDL`

1. Alice `buy()` with `100e8`;
2. Alice `buy()` with `200e8`;

A malicious `saleRecipient` can just not transfer any `CTDL` to the contract and `finalize()` and keep `300e8 WBTC` received.

As a result, Alice and Bob can not get the expected amount of `tokensOut`, and there is no way to retrieve the WBTC paid, in essence, lose all the funds.

### Recommendation

Instead of transferring the tokenIn directing to the `saleRecipient` in `buy()`, consider transferring the tokenIn into the contract (`address(this)`), and require a sufficient amount of `tokenOut` to be transferred into the contract first before the amount of `tokenIn` can be released to the `saleRecipient`.
