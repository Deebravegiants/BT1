# [C] C-01 | Missing Access Control In sendMessage Function

## Summary
Severity: Critical
Contest weight: 0.1290
Dataset id: 2176
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The VaultCrossChainManager contract implements the sendMessage which is used to send cross-chain messages. This function does not implement any type of access control and, therefore, any malicious user can craft arbitrary cross-chain payloads and transmit them causing the receiving chain’s contract logic to execute unverified operations. This could be easily exploited to perform unauthorized withdrawals or deposits.

## Recommendation
Introduce strict access control to sendMessage so that only trusted contracts, such as whitelisted vaults, can invoke cross-chain operations.
