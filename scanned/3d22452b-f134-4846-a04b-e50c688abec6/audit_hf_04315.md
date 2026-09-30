# [H] H-12 | Anchor Liquidity Can Be Removed

## Summary
Severity: High
Contest weight: 0.1320
Dataset id: 21465
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the slide function the anchor position is allocated based on the reserves of the previous anchor.
However the previous anchor may have zero reserves, since it is capped to a maximum width, and the price is able to go below the anchor, between the gap if another actor creates an outside position.
As a result, the slide function will read that the anchor has 0 reserves and assign the new anchor to have 0 reserves and thus 0 liquidity.

## Recommendation
Consider adopting a liquidity based approach to assigning the anchor position in slide rather than a reserves based approach.
