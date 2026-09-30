# [M] M-03 | Wrong Feature Flag Used For Account Split

## Summary
Severity: Medium
Contest weight: 0.0493
Dataset id: 21103
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the splitAccount function the feature flag validation is performed with the
Flags.MERGE_ACCOUNT feature, meanwhile the Flags.SPLIT_ACCOUNT feature ought to be used.
This can allow an account which does not have permission to split their account to do so anyway.

## Recommendation
Validate the feature flag based upon the Flags.SPLIT_ACCOUNT feature in the splitAccount function.
