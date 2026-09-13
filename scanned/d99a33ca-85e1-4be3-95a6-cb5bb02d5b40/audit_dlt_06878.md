# [H] Price feed can be manipulated

## Summary
Severity: High
Chain: Smart contract
Component: 2021-04-marginswap
Published: 2021-04-07
Source: https://github.com/code-423n4/2021-04-marginswap-findings/issues/21
Type: code-finding

## Details
# Vulnerability details

Anyone can trigger an update to the price feed by calling `PriceAware.getCurrentPriceInPeg(token, inAmount, forceCurBlock=true)`.
If the update window has passed, the price will be computed by simulating a Uniswap-like trade with the amounts.
This simulation uses the reserves of the Uniswap pairs which can be changed drastically using flash loans to yield almost arbitrary output amounts, and thus prices.


# Impact

Wrong prices break the core functionality of the contracts such as borrowing on margin, liquidations, etc.


# Recommended mitigation steps

Do not use the Uniswap spot price as the real price.
Uniswaps itself warns against this and instead recommends implementing a [TWAP price oracle](https://uniswap.org/docs/v2/smart-contract-integration/building-an-oracle/) using the `price*CumulativeLast` variables.


# Email address

mail@cmichel.io


# Handle

@cmichelio


# Eth address

0x6823636c2462cfdcD8d33fE53fBCD0EdbE2752ad
