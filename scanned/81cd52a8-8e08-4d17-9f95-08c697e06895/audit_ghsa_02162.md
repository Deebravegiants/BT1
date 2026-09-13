# [C] Double free in sys-info 

## Summary
Severity: Critical
Advisory: GHSA-2f5j-3mhq-xv58
CVE: CVE-2020-36434
CWE: CWE-415
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-2f5j-3mhq-xv58
Type: github-advisory

## Affected
- crates.io: `sys-info` — affected >=0 <0.8.0

## Details
Affected versions of sys-info use a static, global, list to store temporary disk information while running. The function that cleans up this list, DFCleanup, assumes a single threaded environment and will try to free the same memory twice in a multithreaded environment. This results in consistent double-frees and segfaults when calling sys_info::disk_info from multiple threads at once. The issue was fixed by moving the global variable into a local scope.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36434
- https://github.com/FillZpp/sys-info-rs/issues/63
- https://github.com/FillZpp/sys-info-rs
- https://raw.githubusercontent.com/rustsec/advisory-db/main/crates/sys-info/RUSTSEC-2020-0100.md
- https://rustsec.org/advisories/RUSTSEC-2020-0100.html
