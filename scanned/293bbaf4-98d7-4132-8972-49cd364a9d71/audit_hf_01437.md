# [M] Any signature is valid before the issuer address is set

## Summary
Severity: Medium
Contest weight: 0.0823
Dataset id: 7454
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The issuerAddress in the FairLauncher and TokenVault is not set in the constructor and the signature libraries do not check if ecrecover returns address(0). Thus, before the issuerAddress is set, it is possible to forge signatures. This could be problematic for example in the TokenVault as there is no on chain balance tracking, so users may withdraw all the balance. However, this is not very likely because honest users will not deposit in the TokenVault if the issuerAddress has not been set.

## Recommendation
Either set the issuerAddress in the constructor or revert if ecrecover() returns address(0).
