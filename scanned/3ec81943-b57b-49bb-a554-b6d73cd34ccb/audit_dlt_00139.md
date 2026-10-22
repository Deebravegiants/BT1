# [H] ERC165Checker may revert instead of returning false

## Summary
Severity: High
Chain: Solidity
Component: OpenZeppelin/openzeppelin-contracts
CVE: CVE-2022-31170
Published: 2022-07-20
Source: https://github.com/OpenZeppelin/openzeppelin-contracts/security/advisories/GHSA-qh9x-gcfh-pcrw
Type: github-advisory

## Details
### Impact

`ERC165Checker.supportsInterface` is designed to always successfully return a boolean, and under no circumstance revert. However, an incorrect assumption about Solidity 0.8's `abi.decode` allows some cases to revert, given a target contract that doesn't implement EIP-165 as expected, specifically if it returns a value other than 0 or 1.

The contracts that may be affected are those that use `ERC165Checker` to check for support for an interface and then handle the lack of support in a way other than reverting.

### Patches

The issue was patched in 4.7.1.

### References

https://github.com/OpenZeppelin/openzeppelin-contracts/pull/3552

### For more information

If you have any questions or comments about this advisory, or need assistance deploying the fix, email us at [security@openzeppelin.com](mailto:security@openzeppelin.com).
