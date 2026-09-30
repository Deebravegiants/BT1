# [M] Software Execution Timing Side Channel of Secret Signing Key

## Summary
Severity: Medium
Contest weight: 0.0600
Dataset id: 5196
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The group scalar multiplication that makes up the core cryptographic operation of BLS signature is implemented using the arkworks library which currently does not support constant-time elliptic curve / ﬁeld arithmetic. Fine-grained timing of this operation can lead to leakage of the bits of the singing key.

## Recommendation
If the Espresso system admits a channel for untrusted users to time this operation, consider switching to a constant-time group scalar multiplication implementation.
