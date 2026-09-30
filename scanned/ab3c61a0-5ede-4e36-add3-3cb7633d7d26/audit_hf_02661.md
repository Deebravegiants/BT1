# [M] L2Geth Client Private Key Stored Without Encryption

## Summary
Severity: Medium
Contest weight: 0.0674
Dataset id: 14403
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The L2geth node’s private key is stored in cleartext.
The functions SaveECDSA() and LoadECDSA(), which save a private key to file and load a private key from a file respectively make no use of encryption or decryption.
This suggests that the l2geth client’s private key is stored in cleartext. As L2geth is used by Rollup verifiers and other
system actors this is not advisable.

## Recommendation
Do not store sensitive information, such as private keys, in cleartext. Implement encryption for sensitive data at rest.
