# [M] OpenZeppelin Contracts's Cross chain utilities for Arbitrum L2 see EOA calls as cross chain calls

## Summary
Severity: Medium
Chain: Solidity
Component: @openzeppelin/contracts
CVE: CVE-2022-35916
CWE: Incorrect Resource Transfer Between Spheres
Published: 2022-08-14
Source: https://github.com/advisories/GHSA-9j3m-g383-29qr
Type: github-advisory

## Details
### Impact

Contracts using the cross chain utilies for Arbitrum L2, `CrossChainEnabledArbitrumL2` or `LibArbitrumL2`, will classify direct interactions of externally owned accounts (EOAs) as cross chain calls, even though they are not started on L1. This is assessed as low severity because any action taken by an EOA on the contract could also be taken by the EOA through the bridge if the issue was not present.

### Patches

This issue has been patched in v4.7.2.

### References

https://github.com/OpenZeppelin/openzeppelin-contracts/pull/3578

### For more information

If you have any questions or comments about this advisory, or need assistance deploying a fix, email us at [security@openzeppelin.com](mailto:security@openzeppelin.com).
