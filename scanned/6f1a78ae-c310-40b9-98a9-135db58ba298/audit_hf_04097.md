# [M] ORDM-6 | Liquidations Fail On Price Drops

## Summary
Severity: Medium
Contest weight: 0.0715
Dataset id: 20553
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the case of a steep price move (UST for example), the protocol needs to be able to perform liquidations to ensure the system remains solvent. During this volatility, the percentage difference between the lagging EMA and the current price may exceed the market.maxPriceDeviation and revert, causing liquidations to fail.

## Recommendation
Consider simply fetching and utilizing the primaryPrice for liquidation. Because the price feed is updated prior to liquidation, the call priceFeed.getMarketPricePrimary() should not revert. It would also be worth adding a confidence interval when fetching only the primaryPrice to mitigate any potential price manipulation.
