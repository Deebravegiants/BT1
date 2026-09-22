# [M] transpose: Buffer overflow due to integer overflow

## Summary
Severity: Medium
Advisory: GHSA-5gmm-6m36-r7jh
CVE: CVE-2023-53156
CWE: CWE-120, CWE-190
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:C/C:N/I:L/A:L (CVSS_V3)
Published: 2024-04-05
Source: https://github.com/advisories/GHSA-5gmm-6m36-r7jh
Type: github-advisory

## Affected
- crates.io: `transpose` — affected >=0.1.0 <0.2.3

## Details
Given the function `transpose::transpose`:
```rust
fn transpose<T: Copy>(input: &[T], output: &mut [T], input_width: usize, input_height: usize)
```

The safety check `input_width * input_height == output.len()` can fail due to `input_width * input_height` overflowing in such a way that it equals `output.len()`.
As a result of failing the safety check, memory past the end of `output` is written to. This only occurs in release mode since `*` panics on overflow in debug mode.

Exploiting this issue requires the caller to pass `input_width` and `input_height` arguments such that multiplying them overflows, and the overflown result equals the lengths of input and output slices.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-53156
- https://github.com/ejmahler/transpose/issues/11
- https://github.com/ejmahler/transpose/commit/c4bcd39fabca9a31a401d0cc42d4090869b5a37a
- https://github.com/ejmahler/transpose
- https://rustsec.org/advisories/RUSTSEC-2023-0080.html
