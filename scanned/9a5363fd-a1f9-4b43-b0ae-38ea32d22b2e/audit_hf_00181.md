# [M] No bar fees for `IndexPools`?

## Summary
Severity: Medium
Contest weight: 0.0649
Dataset id: 965
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
`IndexPool` doesn’t collect fees for `barFeeTo`. Since this Pool contains also a method `updateBarFee()`, probably this is an unintended behavior. Also without a fee, liquidity providers would probably ditch `ConstantProductPool` in favor of `IndexPool` (using the same two tokens with equal weights), since they get all the rewards. This would constitute an issue for the ecosystem.

## Recommendation
Add a way to send `barFees` to `barFeeTo`, same as the other pools.
