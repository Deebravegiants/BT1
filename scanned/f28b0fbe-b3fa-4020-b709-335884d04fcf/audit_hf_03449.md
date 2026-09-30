# [M] DPCU-2 | priceImpactDiffUsd Paid Before priceImpactUsd

## Summary
Severity: Medium
Contest weight: 0.0912
Dataset id: 18859
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
During an insolvent close, the priceImpactDiffUsd is paid at a higher priority than the negative price impact. This means there are scenarios where the position is liquidated or ADL'd and the account is credited with claimable tokens for price impact that was capped, meanwhile the base price impact, that was the uncapped portion, goes unpaid. Ultimately this benefits the user and hurts the protocol because these funds will become claimable for the user rather than going towards the positionImpactPool and poolAmount to cover as much of the price impact amount as possible.

## Recommendation
Pay the priceImpactUsd before the priceImpactDiffUsd.
