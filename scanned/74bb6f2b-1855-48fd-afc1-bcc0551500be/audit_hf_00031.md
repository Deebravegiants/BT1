# [M] OCL-1 | Risk-Free Trade by Sandwiching Volatility Updates

## Summary
Severity: Medium
Contest weight: 0.0965
Dataset id: 107
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When setStrikeVolatility() function is called, it presents an opportunity for an attacker to see that a volatility change will occur and sandwich attack the transaction. In this sandwich attack, the attacker will front-run the volatility change with a buy and then back-run the volatility change with a sell. By sandwich attacking the transaction, the attacker can profit from the volatility change without exposing themselves to any risk of a price change. This will be a risk-free trade for the attacker at the expense of the LPs.

## Recommendation
Increase fees to ensure that the profits from the attack will be less than the fees incurred. Otherwise consider implementing a two-step execution for trading options on the exchange, where a keeper performs the execution of a trade on the behalf of a user.
