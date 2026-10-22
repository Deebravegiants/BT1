# [M] GMXC-4 | Insolvent Liquidations Revert

## Summary
Severity: Medium
Contest weight: 0.0568
Dataset id: 148
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Insolvent liquidations cannot occur if the Order contract does not have enough to cover the outstanding amount. It is unlikely that positions are able to become insolvent as this would require unexpected immediate price action or inaction from liquidators, however it would be prudent to be able to handle such a case.

## Recommendation
Consider implementing logic such that insolvent positions may be liquidated successfully.
