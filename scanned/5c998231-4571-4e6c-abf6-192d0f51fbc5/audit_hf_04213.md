# [C] C-02 | Splitting Positions Allows fromAccount To Go Below IM

## Summary
Severity: Critical
Contest weight: 0.1823
Dataset id: 21107
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the splitAccount function the toAccount which is created from a portion of the fromAccount is
validated to meet the minimum initial margin requirement, however the fromAccount is not validated
to still uphold the initial margin requirement after the split.
As a result it is possible for the fromAccount to circumvent the minimum initialMargin and create
positions that are prone to insolvent liquidations and create bad debt. Additionally it is possible for a
malicious actor to liquidate their small position that is left behind this way and wind up with a net
profit from the flag and liquidation fee.

## Recommendation
Validate that the fromAccount is still above the initial margin requirement after the split occurs.
