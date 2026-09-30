# [M] Possible Private Key Leakage through Clipboard

## Summary
Severity: Medium
Contest weight: 0.0818
Dataset id: 12206
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
During the process of storing and exporting the private key, we have found a potential risk which may result in the compromise of the private key. Specifically, the wallet allows users to save their private keys to other applications by copying them to the clipboard for easy access. However, a malicious application that has access to the clipboard is able to obtain the private key without being perceived by the user.

## Recommendation
Forbid the behavior of copying the private key. However, for the sake of user experience, we recommend that the user can be clearly informed of the possible risks before choosing to copy the private key, and provide a function to clear the clipboard after the copy.
