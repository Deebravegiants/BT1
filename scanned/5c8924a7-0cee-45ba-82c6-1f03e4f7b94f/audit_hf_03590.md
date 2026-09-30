# [M] SNAP-2 | Untruncated Timestamps Are Unmatchable

## Summary
Severity: Medium
Contest weight: 0.0631
Dataset id: 19569
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In both the find and search functions, the method for validating whether a snapshot has been found or not is to check whether the supplied timestamp is exactly equal to the snapshot timestamp. However, this will rarely be the case as the provided timestamp is not truncated to satisfy the 5-minute intervals that the snapshot timestamps are stored with.

## Recommendation
Truncate the provided timestamp so that it will be much more likely to line up with the snapshot timestamps.
