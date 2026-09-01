# [H] Frontier's modexp precompile is slow for even modulus

## Summary
Severity: High
Chain: pallet-evm-precompile-modexp
Component: pallet-evm-precompile-modexp
CVE: CVE-2023-28431
CWE: Incorrect Calculation
Published: 2023-03-21
Source: https://github.com/advisories/GHSA-fcmm-54jp-7vf6
Type: github-advisory

## Details
### Impact

Frontier's `modexp` precompile uses `num-bigint` crate under the hood. [In the implementation](https://github.com/rust-num/num-bigint/blob/6f2b8e0fc218dbd0f49bebb8db2d1a771fe6bafa/src/biguint/power.rs#L134), the cases for modulus being even and modulus being odd are treated separately. Odd modulus uses the fast Montgomery multiplication, and even modulus uses the slow plain power algorithm. This gas cost discrepancy was not accounted for in the `modexp` precompile, leading to possible denial of service attacks.

### Patches

No fixes for `num-bigint` is currently available, and thus this advisory will be first fixed in the short term by raising the gas costs for even modulus, and in the long term fixing it in `num-bigint` or switching to another modexp implementation.

The short-term fix for Frontier is deployed at [PR 1017](https://github.com/paritytech/frontier/pull/1017).

The recommendations are as follows:

- If you anticipate malicious validators, it's recommended to issue an emergency runtime upgrade as soon as possible.
- If you do not anticipate malicious validators, it's recommended to issue a normal runtime upgrade, as Substrate has builtin timeout protection when validators are building blocks.

### Workarounds

None.

### References

A similar issue was presented in Geth's implementation and the fix can be found [here](https://go-review.googlesource.com/c/go/+/420897).
