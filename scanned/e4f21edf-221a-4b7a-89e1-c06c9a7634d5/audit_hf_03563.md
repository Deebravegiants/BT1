# [M] SIG-1 | Signature Malleability

## Summary
Severity: Medium
Contest weight: 0.0613
Dataset id: 19365
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The verify function uses ecrecover without any validation that the s value is from one half of the valid s range, therefore it is possible for signatures to be maliciously replayed with a different s. At present, the OperatorManager is the only address that can perform this signature malleability, however, the opportunity should be removed.

## Recommendation
Use the OpenZeppelin ECDSA library, which automatically restricts the valid s range, to verify signatures.
