# [M] Compiler optimisation leads to SEGFAULT

## Summary
Severity: Medium
Advisory: GHSA-r6ff-2q3c-v3pv
CWE: CWE-908
Ecosystem: crates.io
CVSS: CVSS:3.0/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-r6ff-2q3c-v3pv
Type: github-advisory

## Affected
- crates.io: `pnet` — affected >=0 <0.27.2

## Details
Affected versions of the `pnet` crate were optimized out by compiler, which caused dereference of uninitialized file descriptor which caused segfault.

## References
- https://github.com/libpnet/libpnet/issues/449
- https://github.com/libpnet/libpnet/pull/455
- https://github.com/libpnet/libpnet
- https://rustsec.org/advisories/RUSTSEC-2019-0037.html
