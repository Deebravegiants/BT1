# [M] Integer underflow in Frontier

## Summary
Severity: Medium
Advisory: GHSA-cjg2-2fjg-fph4
CVE: CVE-2022-21685
CWE: CWE-191
Ecosystem: crates.io
Published: 2022-01-14
Source: https://github.com/advisories/GHSA-cjg2-2fjg-fph4
Type: github-advisory

## Affected
- crates.io: `pallet-evm-precompile-modexp` — affected >=0

## Details
### Impact

A bug in Frontier's MODEXP precompile implementation can cause an integer underflow in certain conditions. This will cause a node crash for debug builds. For release builds (and production WebAssembly binaries), the impact is limited as it can only cause a normal EVM out-of-gas. It is recommended that you apply the patch as soon as possible.

If you do not use MODEXP precompile in your runtime, then you are not impacted.

### Patches

Patches are applied in PR #549.

### Workarounds

None.

### References

Patch PR: #549

### Credits

Thanks to SR-Labs for discovering the security vulnerability, and thanks to PureStake team for the patches.

### For more information

If you have any questions or comments about this advisory:
* Open an issue in the [Frontier repo](https://github.com/paritytech/frontier)

## References
- https://github.com/paritytech/frontier/security/advisories/GHSA-cjg2-2fjg-fph4
- https://nvd.nist.gov/vuln/detail/CVE-2022-21685
- https://github.com/paritytech/frontier/pull/549
- https://github.com/paritytech/frontier/commit/8a93fdc6c9f4eb1d2f2a11b7ff1d12d70bf5a664
- https://github.com/paritytech/frontier
