# [C] Reusing the same rho and pubKey in different deposits leads to lost tokens

## Summary
Severity: Critical
Contest weight: 0.0904
Dataset id: 15188
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The nullifier is formed from rho and the schnorr pubKey. This means that depositing with different assets and amounts will still have the same nullifier, leading to the inability to move the following deposits with the same rho and pubKey. Check the poc here for details.

## Recommendation
Either enforce the nullifier uniqueness (via unique rho and pubkey combination) or use the note as nullifier.
