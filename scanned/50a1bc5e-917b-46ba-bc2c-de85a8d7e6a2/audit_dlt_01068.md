# [M] rs-soroban-sdk: `Fr` scalar field equality comparison bypasses modular reduction

## Summary
Severity: Medium
Chain: soroban-sdk
Component: soroban-sdk, soroban-sdk, soroban-sdk
CVE: CVE-2026-32322
CWE: Incorrect Comparison
Published: 2026-03-13
Source: https://github.com/advisories/GHSA-x2hw-px52-wp4m
Type: github-advisory

## Details
# Security Advisory: Incorrect Equality for Fr Scalar Field Types (BN254, BLS12-381)

## Summary

Missing modular reduction in `Fr` causes incorrect equality comparisons for BN254 and BLS12-381 types in soroban-sdk.

## Impact

The `Fr` (scalar field) types for BN254 and BLS12-381 in `soroban-sdk` compared values using their raw `U256` representation without first reducing modulo the field modulus `r`. This caused mathematically equal field elements to compare as not-equal when one or both values were unreduced (i.e., >= `r`). 

The vulnerability requires an attacker to supply crafted `Fr` values through contract inputs, and compare them directly without going through host-side arithmetic operations.

Smart contracts that rely on `Fr` equality checks for security-critical logic could produce incorrect results. The impact depends on how the affected contract uses Fr equality comparisons, but can result in incorrect authorization decisions or validation bypasses in contracts that perform equality checks on user-supplied scalar values.

## Details

`Fr` types for both curves are wrappers around `U256`. The `PartialEq` implementation compared the raw `U256` values directly. However, the constructors (`from_u256`, `from_bytes`, `From<U256>`) accepted arbitrary `U256` values without reducing them modulo `r`. This meant two `Fr` values representing the same field element (e.g., `1` and `r + 1`) could have different internal representations and compare as not-equal.

This issue was compounded by an asymmetry: all host-side arithmetic operations (`fr_add`, `fr_sub`, `fr_mul`, `fr_pow`, `fr_inv`) always return canonically reduced results in `[0, r)`, while user-constructed `Fr` values could hold unreduced representations. Comparing a user-supplied `Fr` against a host-computed `Fr` would therefore produce incorrect results even when the underlying field elements were identical.

### Example

```rust
let r = /* BN254 scalar field modulus */;
let a = Fr::from_u256(r + 1); // unreduced, stores r+1
let b = Fr::from_u256(1);     // reduced, stores 1

// a and b represent the same field element (1), but compared as NOT equal
assert_eq!(a, b); // FAILED before the fix
```

## Patches

All `Fr` construction paths now reduce the input modulo `r`, ensuring a canonical representation in `[0, r)`. This guarantees that equal field elements always have identical internal representations, making the existing `PartialEq` comparison correct.

Additionally, `Fp` and `Fp2` base field types for both curves now validate that values are strictly less than the field modulus on construction, rejecting out-of-range inputs.

## Workarounds

_Trimmed to 38 lines — full report: https://github.com/advisories/GHSA-x2hw-px52-wp4m_
