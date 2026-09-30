# [M] Minting public vault shares while the proto-

## Summary
Severity: Medium
Contest weight: 0.1106
Dataset id: 17742
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Assets can be deposited into public vaults by LPs with PublicVault.mint function to bypass a possible paused protocol. The PublicVault contract prevents calls to the PublicVault.deposit function while the protocol is paused by using the whenNotPaused modifier. The PublicVault contract extends the ERC4626Cloned contract, which has two functions to deposit assets into the vault: the deposit function and the mint function. The latter function, however, is not overwritten in the PublicVault contract and therefore lacks the appropriate whenNotPaused modifier. LPs can deposit assets into public vaults with the PublicVault.mint function to bypass a possible paused protocol. This can lead to LP fund loss depending on the

## Recommendation
Override the mint function and add the whenNotPaused modifier
