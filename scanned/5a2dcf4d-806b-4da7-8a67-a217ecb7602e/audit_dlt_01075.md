# [M] ethereum does not check transaction malleability for EIP-2930, EIP-1559 and EIP-7702 transactions

## Summary
Severity: Medium
Chain: ethereum
Component: ethereum
CVE: CVE-2025-53359
CWE: Improper Check for Unusual or Exceptional Conditions
Published: 2025-07-02
Source: https://github.com/advisories/GHSA-3w94-vq2x-v5wr
Type: github-advisory

## Details
### Impact

Prior to `ethereum` crate v0.18.0, signature malleability (according to EIP-2) was only checked for "legacy" transactions, but not for EIP-2930, EIP-1559 and EIP-7702 transactions.

This is a specification deviation and therefore a high severity advisory if the `ethereum` crate is used for Ethereum mainnet. Note that signature malleability itself is not a security issue, and therefore if the `ethereum` crate is used on a single-implementation blockchain, it's a low/informational severity advisory.

### Patches

The issue is fixed in `ethereum` v0.18.0

### Workarounds

You can also manually check transaction malleability outside of the crate. But it's recommended to simply upgrade the version.

### References

See PR: https://github.com/rust-ethereum/ethereum/pull/67
