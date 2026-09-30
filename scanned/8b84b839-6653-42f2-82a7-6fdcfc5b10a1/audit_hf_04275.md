# [H] H-07 | MarketSwap Orders May Use Unexpected Prices

## Summary
Severity: High
Contest weight: 0.1070
Dataset id: 21414
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the processOrder function for swap orders, the price timestamp validation includes no maxOracleTimestamp validation for MarketSwap orders. As a result a keeper may accidentally or maliciously execute a MarketSwap order when it is far past its request expiration age, with prices that are significantly unfavorable for the user.

## Recommendation
When executing a MarketSwap order be sure to validate that the maxOracleTimestamp is not above the order’s requestExpirationTime.
