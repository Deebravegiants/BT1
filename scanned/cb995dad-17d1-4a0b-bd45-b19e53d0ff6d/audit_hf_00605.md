# [M] M-03 | DISCOVERY_LENGTH Hardcoded For 1% Fee Pools

## Summary
Severity: Medium
Contest weight: 0.0585
Dataset id: 2104
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The DISCOVERY_LENGTH variable in the MarketMaking contract is intended to represent 30 tick
spacings, as indicated by the comment.
However, its current implementation as 30 x 200 only aligns with 1% fee pools. This means the
calculation will be incorrect if applied to pools with different fee tiers.

## Recommendation
If the protocol intends to only use 1% fee pools, no changes are needed. Otherwise, it should obtain
the correct tick spacing from the BPOOLv1 contract instead.
