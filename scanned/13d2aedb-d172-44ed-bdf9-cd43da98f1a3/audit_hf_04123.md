# [M] GLOBAL-5 | Anyone Can Remove All LST Deposits From A Strategy

## Summary
Severity: Medium
Contest weight: 0.0755
Dataset id: 20583
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Anyone can force the system to withdraw the entirety of any specific asset from Eigenlayer by depositing a different asset and then using the withdrawUsingEigenShares function to queue a withdrawal for the vaults entire strategy shares. This way the Rest system would be unable to earn yield and may not be eligible for an airdrop. A competing LST protocol may do this to gain their own position in a strategy that has maximum TVL limits.

## Recommendation
Consider implementing a mechanism to prevent malicious actors from removing the Vault's allocation in strategies.
