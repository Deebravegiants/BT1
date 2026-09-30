# [M] Potential Panic in AVX2 SHAKE-256

## Summary
Severity: Medium
Advisory: RUSTSEC-2026-0208
Ecosystem: crates.io
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-05-21
Source: https://osv.dev/vulnerability/RUSTSEC-2026-0208
Type: osv

## Affected
- crates.io: `libcrux-sha3` — affected >=0.0.0-0 <0.0.10

## Details
The AVX2-optimized implementation of SHAKE-256 intended for use in
ML-KEM and ML-DSA would panic if the length of the output buffers was
greater than 32 and not a multiple of 8, due to an out-of-bounds
indexing operation.

## Impact
This bug impacts users on AVX2 platforms that use the
`libcrux_sha3::avx2::x4::shake256` API outside of ML-KEM or ML-DSA
with output buffers of length `> 32` and not divisible by `8`. It does
not impact the use in ML-KEM or ML-DSA because there output buffer
lengths are always divisible by `8`.

## Mitigation
Starting from version `0.0.10`, the AVX2-optimized SHAKE-256 will no
longer panic on output buffer lengths `> 32` that are not divisible by
`8`.

## References
- https://crates.io/crates/libcrux-sha3
- https://rustsec.org/advisories/RUSTSEC-2026-0208.html
- https://github.com/celabshq/libcrux/pull/1456
