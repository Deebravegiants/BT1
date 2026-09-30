# [M] Signatures Validated to be On-Curve

## Summary
Severity: Medium
Contest weight: 0.0524
Dataset id: 5186
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
For all veriﬁcation methods, verify, aggregate_verify, and multi_sig_verify, if the signature is not checked to be on-curve (or in the appropriate large prime-order) subgroup of the elliptic curve then various "low-order" attacks can be used to leak information about the secret key.

## Recommendation
For BN254, a subgroup check in G1 is not needed, but an inexpensive on-curve check is still important.
