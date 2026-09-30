# [M] M-04 | ExitVaultEntryPoint Centralizes Governance Power Instead Of Delegating To ExitVault Owners

## Summary
Severity: Medium
Contest weight: 0.1176
Dataset id: 2046
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the current design of the ExitVaultEntryPoint and ExitVault contracts, the governance power associated with the staked GMX tokens is centralized within the ExitVaultEntryPoint contract’s treasury rather than being held by the individual ExitVault owners. When users deposit their GMX tokens into an ExitVault, the tokens are staked under the contract's address, and the resulting voting power accumulates to the ExitVaultEntryPoint’s treasury. This setup means that all the governance rights derived from these staked tokens are controlled by the ExitVaultEntryPoint’s treasury rather than the actual owners of the tokens. Consequently, the vault owners are deprived of their ability to participate in governance decisions proportionally to their stake.

## Recommendation
Consider updating the ExitVault contract so it delegates the governance power to the individual ExitVault owners.
