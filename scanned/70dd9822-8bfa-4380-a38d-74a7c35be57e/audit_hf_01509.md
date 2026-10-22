# [M] M-3 Unsafe transfer

## Summary
Severity: Medium
Contest weight: 0.0447
Dataset id: 8005
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Some of the tokens do not revert on an unsuccessful transfer. We recommend using the OZ safeTransfer method instead of a basic transfer method.
FantiumNFTV3.sol#L409-L413
FantiumNFTV3.sol#L417-L421
FantiumClaimingV1.sol#L591
FantiumClaimingV1.sol#L595

## Recommendation
We recommend using the OpenZeppelin safeTransfer library.
