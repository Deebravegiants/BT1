# [M] Missing Address Protection

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description

While MetaMask hides wallet addresses by default, requiring users to expose them to dapps manually, the snap's `fil_getAddress` and `fil_getAccountInfo` RPC endpoints always disclose the current address to any connected dapp, even if that address has not been connected to the page. This allows potentially untrusted dapps to silently retrieve all user addresses, bypassing MetaMask's intentional security design.

#### Recommendation

Adopt security protocols similar to MetaMask's main wallet. Let users select which addresses they share with dapps and prevent automatic exposure of non-allowlisted wallet addresses without explicit user permission.
