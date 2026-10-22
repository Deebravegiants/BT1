# [M] The RedstoneCoreOracle has a constant STALE_PRICE_THRESHOLD for all tokens

## Summary
Severity: Medium
Contest weight: 0.1218
Dataset id: 23150
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Different tokens have different STALE_PRICE_THRESHOLD. The protocol uses a constant STALE_PRICE_THRESHOLD=3600 for all tokens in the RedstoneCoreOracle.
The issue arises when the token actually has a STALE_PRICE_THRESHOLD < 3600. Here are some tokens whose redstone priceFeed has a STALE_PRICE_THRESHOLD < 3600 (1 hour):
1. TRX/USD 10 minutes
2. BNB/USD 1 minute
Using a constant STALE_PRICE_THRESHOLD=3600, rather than setting one for each token.
Internal pre-conditions
External pre-conditions
Token has a threshold < 3600
Attack Path
Stale prices.
It will lead to unfair liquidations due to stale price valuation of collateral AND/OR a position not being liquidated due to stale price valuation of collateral.
It will also lead to borrowing a wrong amount due to stale price valuation of collateral.

## Recommendation
Set a unique STALE_PRICE_THRESHOLD for each token, similar to the chainlink oracle.
