# [M] Integer underflow in Frontier

## Summary
Severity: Medium
Chain: pallet-evm-precompile-modexp
Component: pallet-evm-precompile-modexp
CVE: CVE-2022-21685
CWE: Integer Underflow (Wrap or Wraparound)
Published: 2022-01-14
Source: https://github.com/advisories/GHSA-cjg2-2fjg-fph4
Type: github-advisory

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
