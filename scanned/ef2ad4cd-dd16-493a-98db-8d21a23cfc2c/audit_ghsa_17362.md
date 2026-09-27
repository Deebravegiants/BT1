# [H] libcrux incorrectly calculates on aarch64

## Summary
Severity: High
Advisory: GHSA-2cgv-28vr-rv6j
CWE: CWE-200, CWE-327
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-12-04
Source: https://github.com/advisories/GHSA-2cgv-28vr-rv6j
Type: github-advisory

## Affected
- crates.io: `libcrux-intrinsics` — affected >=0.0.3 <0.0.4
- crates.io: `libcrux-ml-kem` — affected >=0.0.3 <0.0.4
- crates.io: `libcrux-ml-dsa` — affected >=0.0.3 <0.0.4

## Details
On platforms without the `core::arch::aarch64::vxarq_u64` intrinsic, an unverified fallback in `libcrux-intrinsics` v0.0.3
passed incorrect arguments and produced wrong results. This corrupted SHA-3 digests and caused `libcrux-ml-kem` and
`libcrux-ml-dsa` to sample incorrectly, yielding incorrect shared secrets and invalid signatures.

The issue has been fixed in v0.0.4.

## References
- https://github.com/cryspen/libcrux/issues/1220
- https://github.com/cryspen/libcrux/pull/1222
- https://github.com/cryspen/libcrux/commit/8d10f45631afd1d93fabb2278dbb388a075b5608
- https://github.com/cryspen/libcrux
- https://rustsec.org/advisories/RUSTSEC-2025-0133.html
