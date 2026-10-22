# [H] Price feed can be manipulated

## Summary
Severity: High
Contest weight: 0.1943
Dataset id: 230
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Anyone can trigger an update to the price feed by calling `PriceAware.getCurrentPriceInPeg(token, inAmount, forceCurBlock=true)`. If the update window has passed, the price will be computed by simulating a Uniswap-like trade with the amounts. This simulation uses the reserves of the Uniswap pairs which can be changed drastically using flash loans to yield almost arbitrary output amounts, and thus prices. Wrong prices break the core functionality of the contracts such as borrowing on margin, liquidations, etc.

Recommend against using the Uniswap spot price as the real price. Uniswap itself warns against this and instead recommends implementing a [TWAP price oracle](https://uniswap.org/docs/v2/smart-contract-integration/building-an-oracle/) using the `price*CumulativeLast` variables.

## Recommendation
No recommendation
