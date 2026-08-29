# [M] GovernorCompatibilityBravo may trim proposal calldata

## Summary
Severity: Medium
Chain: Solidity
Component: OpenZeppelin/openzeppelin-contracts
CVE: CVE-2023-30542
Published: 2023-04-13
Source: https://github.com/OpenZeppelin/openzeppelin-contracts/security/advisories/GHSA-93hq-5wgc-jc82
Type: github-advisory

## Details
### Impact

The proposal creation entrypoint (`propose`) in `GovernorCompatibilityBravo` allows the creation of proposals with a `signatures` array shorter than the `calldatas` array. This causes the additional elements of the latter to be ignored, and if the proposal succeeds the corresponding actions would eventually execute without any calldata. The `ProposalCreated` event correctly represents what will eventually execute, but the proposal parameters as queried through `getActions` appear to respect the original intended calldata.

### Patches

This issue has been patched in v4.8.3.

### Workarounds

Ensure that all proposals that pass through governance have equal length `signatures` and `calldatas` parameters.
