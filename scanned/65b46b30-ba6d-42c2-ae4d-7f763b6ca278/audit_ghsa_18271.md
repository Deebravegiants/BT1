# [H] toodee is vulnerable to Heap Buffer Overflow through its DrainCol Destructor

## Summary
Severity: High
Advisory: GHSA-pfp7-vxgr-83pw
CWE: CWE-122
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:H/SC:L/SI:L/SA:L (CVSS_V4)
Published: 2025-09-09
Source: https://github.com/advisories/GHSA-pfp7-vxgr-83pw
Type: github-advisory

## Affected
- crates.io: `toodee` — affected >=0.2.0 <0.6.0

## Details
An off-by-one error in the `DrainCol::drop` destructor could cause an unsafe memory copy operation to exceed the bounds of the associated vector.

The error was related to the size of the data being copied in one of the `ptr::copy` invocations inside the destructor.

When removing the first column from a TooDee object, the DrainCol return object could cause a heap buffer overflow vulnerability when it is dropped.

The issue was fixed in commit `e6e16d5` by reducing the copied size by one.

## References
- https://github.com/antonmarsden/toodee/issues/26
- https://github.com/antonmarsden/toodee/commit/e6e16d5a97e6258ffbedbae1bde65b45c60f242f
- https://github.com/antonmarsden/toodee
- https://rustsec.org/advisories/RUSTSEC-2025-0062.html
