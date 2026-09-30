# [H] GMOCL-1 | longToken Assumed To Be The indexToken

## Summary
Severity: High
Contest weight: 0.1027
Dataset id: 147
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the _get function the price of the long token provided is the price of the index token, however not all GM markets have the long token as the index token. For example, the DOGE/USD GM market has Ether as its long token. In this case the price of ETH is provided as the price of DOGE which will be dramatically inaccurate.

## Recommendation
Treat the long token separately from the index token, as these two are not guaranteed to be the same.
