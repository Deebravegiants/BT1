# [M] VAULTM-1 | Funds Will Be Locked On Hard Fork

## Summary
Severity: Medium
Contest weight: 0.0754
Dataset id: 19363
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the VaultManager contract, token balances are stored in mappings such as tokenBalanceOnchain or tokenFrozenBalanceOnchain. These mappings take a token hash and a chainID and point to a token balance. If a chain were to experience a hard fork that chainID will change. This will result in the token balance being inaccessible as there will be a difference between what is being stored in state and the actual chainID of the chain.

## Recommendation
Add an onlyOwner restricted function that will allow the protocol to migrate balances from the old chainID to the new chainID.
