# [M] ERC165Checker unbounded gas consumption

## Summary
Severity: Medium
Chain: Solidity
Component: OpenZeppelin/openzeppelin-contracts
CVE: CVE-2022-35915
Published: 2022-07-28
Source: https://github.com/OpenZeppelin/openzeppelin-contracts/security/advisories/GHSA-7grf-83vw-6f5x
Type: github-advisory

## Details
### Impact

The target contract of an EIP-165 `supportsInterface` query can cause unbounded gas consumption by returning a lot of data, while it is generally assumed that this operation has a bounded cost.

### Patches

The issue has been fixed in v4.7.2.

### References

https://github.com/OpenZeppelin/openzeppelin-contracts/pull/3587

### For more information

If you have any questions or comments about this advisory, or need assistance deploying a fix, email us at [security@openzeppelin.com](mailto:security@openzeppelin.com).
