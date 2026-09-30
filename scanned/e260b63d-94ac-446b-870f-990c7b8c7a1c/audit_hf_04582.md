# [M] M-15 | Feeds With > 18 Decimals Are Problematic

## Summary
Severity: Medium
Contest weight: 0.0565
Dataset id: 22185
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The price returned by the oracle is adjusted to 18 decimals with the following computation: _price18 = uint256(_price) * (10 ** 18 / 10 ** _decimals); Notice that the division here happens before the multiplication. This means that if the decimals of the feed are more than 18, the price will be rounded to 0 causing big problems for the assets pricing.

## Recommendation
Multiply price by 1e18 and divide afterwards.
