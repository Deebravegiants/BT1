# [H] H-02 | depositToStrategy Function Will Always Revert

## Summary
Severity: High
Contest weight: 0.1193
Dataset id: 2213
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The depositToStrategy function sends a deposit request to the dexVault via IDexVault(dexVault).depositTo(...), transferring USDC (or another token) in the process. However, there is no approval step for the vault to pull tokens from this contract. Without an ERC-20 approve call, the dexVault has no permission to transfer tokens on behalf of the ProtocolVault. As a result, the deposit call will always revert.

## Recommendation
Approve the dexVault before calling the depositTo function.
