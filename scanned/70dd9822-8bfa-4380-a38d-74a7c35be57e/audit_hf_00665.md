# [M] M-12 | Enabling Tokens Breaks Protocol

## Summary
Severity: Medium
Contest weight: 0.0842
Dataset id: 2201
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
ProtocolVault.setAllowedToken() lets the owner of the contract enable or disable a new token for deposits. When users perform deposits with this token, they will pay an amount of that token. However, the whole system currently is setup to work with USDC. For example, _getOperationData hardcodes the tokenHash to USDC_HASH. If another token were to be enabled, users will be charged that token, but their balance of the USDC token will be increased on the Ledger side instead.

## Recommendation
If you should support multiple tokens, consider not hardcoding the token hashes. Be careful with this approach because some tokens may have different decimals across chains.
