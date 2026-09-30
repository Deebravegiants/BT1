# [M] GLOBAL-1 | Positive Impact Misrepresented

## Summary
Severity: Medium
Contest weight: 0.0735
Dataset id: 18891
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
During both increase and decrease orders, forPositiveImpact is determined based upon the priceImpactUsd being greater than 0, however this is based on the priceImpactUsd after it has been capped. In the event that the position impact pool is empty and the positive price impact value is capped to 0, the fees will be calculated with a forPositiveImpact of false, meanwhile the action does indeed balance the pool.

## Recommendation
Compute forPositiveImpact before the price impact is capped so that actions that balance the pool receive the corresponding conﬁgured fees.
