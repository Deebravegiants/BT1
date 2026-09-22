# [H] libcrux-sha3: Incorrect output from SHAKE squeeze functions

## Summary
Severity: High
Advisory: GHSA-q29p-9pfr-j652
CWE: CWE-682
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-26
Source: https://github.com/advisories/GHSA-q29p-9pfr-j652
Type: github-advisory

## Affected
- crates.io: `libcrux-sha3` — affected >=0 <0.0.8

## Details
The incremental squeeze functions in the portable SHAKE XOF API, when attempting to squeeze more than `RATE` (168 for SHAKE128, 136 for SHAKE256) bytes, performed an additional permutation of the state before producing the first output block, thus discarding the first block of `RATE` bytes of valid XOF output.

## Impact
This bug impacts users that rely on this XOF API to squeeze more than `RATE` bytes. It does not impact the use of libcrux-sha3 in libcrux-ml-kem or libcrux-ml-dsa.

## Mitigation
Starting from version `0.0.8` the squeeze functions correctly output all blocks including the first block.

## References
- https://github.com/cryspen/libcrux/pull/1352
- https://github.com/cryspen/libcrux
- https://rustsec.org/advisories/RUSTSEC-2026-0074.html
