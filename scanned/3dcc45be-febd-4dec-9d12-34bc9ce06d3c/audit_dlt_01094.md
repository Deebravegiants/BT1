# [M] Validity check missing in Frontier

## Summary
Severity: Medium
Chain: pallet-ethereum
Component: pallet-ethereum
CVE: CVE-2021-41138
CWE: Improper Input Validation
Published: 2021-10-13
Source: https://github.com/advisories/GHSA-vj62-g63v-f8mf
Type: github-advisory

## Details
### Impact

In the newly introduced signed Frontier-specific extrinsic for `pallet-ethereum`, a large part of transaction validation logic was only called in transaction pool validation, but not in block execution. Malicious validators can take advantage of this to put invalid transactions into a block.

The attack is limited in that the signature is always validated, and the majority of the validation is done again in the subsequent `pallet-evm` execution logic. However, do note that a chain ID replay attack was possible. In addition, spamming attacks are of main concerns, while they are limited by Substrate block size limits and other factors.

### Patches

The issue is patched in commit 146bb48849e5393004be5c88beefe76fdf009aba.

### References

Patch PR: https://github.com/paritytech/frontier/pull/495

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [Frontier repo](https://github.com/paritytech/frontier/issues)

### Special thanks

Special thanks to @librelois, @nanocryk and the Moonbeam team for reporting and fixing this security vulnerability.
