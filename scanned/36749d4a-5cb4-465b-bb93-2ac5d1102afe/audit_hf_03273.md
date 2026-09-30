# [M] A comment in Syndicate.sol states

## Summary
Severity: Medium
Contest weight: 0.0481
Dataset id: 17967
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A comment in Syndicate.sol states that “Basically, under a rage quit or voluntary withdrawal from the beacon chain, the knot kick is auto-propagated to syndicate”. However, when a KNOT is inactive, the KNOT can still remain part of the syndicate and isn’t automatically removed from the syndicate.

## Recommendation
No recommendation
