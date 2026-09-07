# [M] Transaction validity oversight in pallet-ethereum

## Summary
Severity: Medium
Chain: pallet-ethereum
Component: pallet-ethereum
CVE: CVE-2021-39193
CWE: Improper Input Validation, Improper Validation of Specified Quantity in Input
Published: 2021-09-01
Source: https://github.com/advisories/GHSA-hw4v-5x4h-c3xm
Type: github-advisory

## Details
### Impact

A bug in `pallet-ethereum` can cause invalid transactions to be included in the Ethereum block state in `pallet-ethereum` due to not validating the input data size. Any invalid transactions included this way have no possibility to alter the internal Ethereum or Substrate state. The transaction will appear to have be included, but is of no effect as it is rejected by the EVM engine. The impact is further limited by Substrate extrinsic size constraints.

### Patches

Patches are applied in PR #465.

### Workarounds

None.

### References

Patch PR: https://github.com/paritytech/frontier/pull/465

### For more information

If you have any questions or comments about this advisory:
* Open an issue in the [Frontier repo](https://github.com/paritytech/frontier)
