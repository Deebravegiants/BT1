# [H] FUSE-Rust: Uninitalized memory read and leak caused by fuser crate

## Summary
Severity: High
Advisory: GHSA-cvmj-47v9-35m9
CWE: CWE-908
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-09-15
Source: https://github.com/advisories/GHSA-cvmj-47v9-35m9
Type: github-advisory

## Affected
- crates.io: `fuser` — affected >=0 <0.16.0

## Details
During the creation of a new libfuse session with `fuse_session_new`, the operation list was passed as NULL incorrectly. libfuse expects this argument to always point to list of operations. This caused uninitialized memory read and leaks in libfuse.so.

## References
- https://github.com/cberner/fuser/pull/390
- https://github.com/cberner/fuser
- https://rustsec.org/advisories/RUSTSEC-2021-0154.html
