# [M] M-1 Metapool doesn't allow basepools with len(coins) > 3

## Summary
Severity: Medium
Contest weight: 0.0509
Dataset id: 7123
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The current implementation of the metapool doesn't allow basepools with more than 3 tokens CurveStableSwapMetaNG.vy#L64-L68 but such basepools can be added in the factory. If metapool will be created with basepool with more than 3 tokens, part of the metapool functionality will not work.

## Recommendation
We recommend adding a check in the constructor that BASENCOINS < 4.
