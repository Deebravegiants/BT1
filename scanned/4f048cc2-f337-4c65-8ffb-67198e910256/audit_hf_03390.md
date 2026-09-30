# [M] DOU-1 | Minimum Output Amount Griefing

## Summary
Severity: Medium
Contest weight: 0.0846
Dataset id: 18498
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A malicious actor can observe a user’s triggerPrice for their stop-loss (among other order types)
approaching and shift price impact in the user’s market (or in the user’s virtual inventory) such that
their minimum output becomes invalidated and the order gets canceled.
In some cases this could cause significant grief to users who would have otherwise exited the
market. A malicious actor may stand to benefit from this by holding MarketTokens and grieving
traders within that market.

## Recommendation
Document this behavior clearly to users. Monitor such manipulations and disincentivize them
accordingly by adjusting the price impact factors as necessary.
