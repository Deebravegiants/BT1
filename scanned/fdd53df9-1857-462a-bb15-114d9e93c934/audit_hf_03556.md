# [M] VAULT-1 | Allowed Token Contract Address Added

## Summary
Severity: Medium
Contest weight: 0.0890
Dataset id: 19358
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The documentation for setAllowedToken states that the function is supposed to “Add contract address for an allowed token given the tokenHash.” However, setAllowedToken only adds or removes the tokenHash from the allowedTokenSet. As a result, the address for the token is never added to the allowedToken mapping. Deposits and withdrawals will revert as the zero address does not have function safeTransferFrom, and continue to revert until changeTokenAddressAndAllow is called, which according to the documentation is an "unusual case on Mainnet".

## Recommendation
Add a parameter for the token address and perform allowedToken[_tokenHash]=_tokenAddress.
