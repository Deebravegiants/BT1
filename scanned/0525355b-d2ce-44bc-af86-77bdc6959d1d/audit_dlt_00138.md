# [M] SignatureChecker may revert on invalid EIP-1271 signers

## Summary
Severity: Medium
Chain: Solidity
Component: OpenZeppelin/openzeppelin-contracts
CVE: CVE-2022-31172
Published: 2022-07-20
Source: https://github.com/OpenZeppelin/openzeppelin-contracts/security/advisories/GHSA-4g63-c64m-25w9
Type: github-advisory

## Details
### Impact

`SignatureChecker.isValidSignatureNow` is not expected to revert. However, an incorrect assumption about Solidity 0.8's `abi.decode` allows some cases to revert, given a target contract that doesn't implement EIP-1271 as expected.

The contracts that may be affected are those that use `SignatureChecker` to check the validity of a signature and handle invalid signatures in a way other than reverting. We believe this to be unlikely.

### Patches

The issue was patched in 4.7.1.

### References

https://github.com/OpenZeppelin/openzeppelin-contracts/pull/3552

### For more information

If you have any questions or comments about this advisory, or need assistance deploying the fix, email us at [security@openzeppelin.com](mailto:security@openzeppelin.com).
