# [M] Duplicated execution of subcalls in v4.9.4

## Summary
Severity: Medium
Chain: Solidity
Component: OpenZeppelin/openzeppelin-contracts
CVE: CVE-2023-49798
Published: 2023-12-08
Source: https://github.com/OpenZeppelin/openzeppelin-contracts/security/advisories/GHSA-699g-q6qh-q4v8
Type: github-advisory

## Details
### Context
Merge conflict resolution issue when porting the v5.0.1 `Multicall` update to the v4.9 branch caused a duplicated line.

### Impact
Versions using `Multicall` from `@openzeppelin/contracts@4.9.4` and `@openzeppelin/contracts-upgradeable@4.9.4` will execute each subcall twice. Concretely, this exposes a user to unintentionally duplicate operations like asset transfers.

### Patches
The duplicated `delegatecall` was removed in 4.9.5. The 4.9.4 version is marked as deprecated.
