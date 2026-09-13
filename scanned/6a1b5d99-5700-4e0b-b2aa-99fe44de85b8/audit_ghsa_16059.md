# [M] `simd-json-derive` vulnerable to `MaybeUninit` misuse

## Summary
Severity: Medium
Advisory: GHSA-pqpw-89w5-82v5
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2024-11-12
Source: https://github.com/advisories/GHSA-pqpw-89w5-82v5
Type: github-advisory

## Affected
- crates.io: `simd-json-derive` — affected >=0 <0.12.0

## Details
An invalid use of `MaybeUninit::uninit().assume_init()` in `simd-json-derive`'s derive macro can cause undefined behavior. The original code used `MaybeUninit` to avoid initialisation of the struct and then set the fields using `ptr::write`. The undefined behavior triggered by this misuse of `MaybeUninit` can lead to invlaid memory access and panics in binaries compiled in release mode (aka simd-json-derive prior to version 0.12 has UB and optimizes into some nonsense)

The version `0.12.0` removes this section of code, avoiding the use of MaybeUninit alltogether.

## References
- https://github.com/simd-lite/simd-json-derive/issues/67
- https://github.com/simd-lite/simd-json-derive
- https://rustsec.org/advisories/RUSTSEC-2023-0087.html
