# [M] RsaVerifyOptimized sets the size of the key to 1024 bits, which is unsafe

## Summary
Severity: Medium
Contest weight: 0.0606
Dataset id: 9321
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
RSA signatures rely on the size of the key for higher safety assurances. As computational power advances, it becomes possible to brute force signatures up to more bits. This article indicates keys up to 829 bits have been cracked, which is dangerously close to the hardcoded 1024 bits. The original RsaVerifyOptimized repository recommends setting a key size of at least 2048 bits.

## Recommendation
Update the key size to be 2048.
