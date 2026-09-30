# [M] FEED-1 | Price May Be 0

## Summary
Severity: Medium
Contest weight: 0.3873
Dataset id: 20562
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The price returned by Pyth is checked to be non-zero, however the priceUsd may become 0 after decimal adjustment:
```solidity
priceUsd = SafeCast.toUint256(pythPrice.price) / (10 ** adjustedExpo);
```
For example, if the pythPrice.price = 1 and the pythPrice.expo = -9, then priceUsd = 1 / 10 = 0. Key protocol actions such as liquidations will fail because _verifyAndUpdatePrice calculates the price deviation between primary and secondary price with uint256 diffBps = (_getDiff(primaryPrice, secondaryPrice) * PRECISION_MULTIPLIER) / secondaryPrice; and there will be division by zero.

## Recommendation
Carefully select which assets are supported for trading, as assets with a low price and a large, negative exponent are susceptible to this issue. Furthermore, validate the price is non-zero after conversion to FEED_DECIMALS.
