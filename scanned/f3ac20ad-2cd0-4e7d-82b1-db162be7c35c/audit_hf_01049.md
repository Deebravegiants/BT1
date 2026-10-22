# [H] MJR-4 Blocked LP tokens on contract

## Summary
Severity: High
Contest weight: 0.0282
Dataset id: 4018
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
At the line UniswapMarketMaker.sol#L85 contract changes incoming token to another one, while transferring contract sends all remaining incoming tokens to _recipient, but contract never check remaining incoming <> support LP tokens on contract side. That tokens cannot be rescued anymore after changing incoming.

## Recommendation
We recommend to remove all liquidity before changing incoming token
