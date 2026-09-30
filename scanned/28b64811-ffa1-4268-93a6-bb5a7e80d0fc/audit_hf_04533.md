# [M] M-14 | validDistributorExists Not Checked

## Summary
Severity: Medium
Contest weight: 0.0472
Dataset id: 22097
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The modifyCollateral function calls validDistributorExists which returns a boolean that indicates if a
distributor of the given collateral is set or not.
The modifyCollateral does not check if the returned boolean is true or false. Therefore if no
distributor is set, the flow will continue.

## Recommendation
Revert if the distributor was not set.
