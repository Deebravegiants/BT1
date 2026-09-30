# [M] M-14 | Tick Modulus Hardcoded For Fee Tier

## Summary
Severity: Medium
Contest weight: 0.0605
Dataset id: 2004
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
_calculateTickBounds() uses modulus 200 in order to set the target tick value to the closest acceptable tick range. However, Foil is compatible with multiple fee tiers, but the value 200 is not. For instance, the 0.3% fee tier uses a tick spacing of 60, which is not a divisor of 200. This will cause a revert when attempting to create the epoch.

## Recommendation
Instead of hardcoding 200, use the appropriate value for the fee tier of the pool.
