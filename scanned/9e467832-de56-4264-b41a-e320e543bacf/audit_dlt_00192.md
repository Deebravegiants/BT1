# [M] OpenZeppelin Contracts TransparentUpgradeableProxy clashing selector calls may not be delegated

## Summary
Severity: Medium
Chain: Solidity
Component: @openzeppelin/contracts
CVE: CVE-2023-30541
CWE: Interpretation Conflict
Published: 2023-04-17
Source: https://github.com/advisories/GHSA-mx2q-35m2-x2rh
Type: github-advisory

## Details
### Impact

A function in the implementation contract may be inaccessible if its selector clashes with one of the proxy's own selectors. Specifically, if the clashing function has a different signature with incompatible ABI encoding, the proxy could revert while attempting to decode the arguments from calldata.

The probability of an accidental clash is negligible, but one could be caused deliberately.

### Patches

The issue has been fixed in v4.8.3.

### Workarounds

If a function appears to be inaccessible for this reason, it may be possible to craft the calldata such that ABI decoding does not fail at the proxy and the function is properly proxied through.

### References

https://github.com/OpenZeppelin/openzeppelin-contracts/pull/4154
