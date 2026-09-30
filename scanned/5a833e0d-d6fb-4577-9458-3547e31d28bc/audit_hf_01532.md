# [M] M-3 The _getFee function is not monotonic

## Summary
Severity: Medium
Contest weight: 0.0561
Dataset id: 8157
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
According to the developer's statement, the _getFee function is intended to be monotonic. However, the
current implementation might not be monotonic if several fee tiers are conﬁgured. This issue cannot be
corrected by any conﬁguration due to the nature of the current implementation of the _getFee function.

## Recommendation
We recommend adjusting the implementation of the _getFee function to comply with the intended
behavior.
