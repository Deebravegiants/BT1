# [M] Data races in lock_api

## Summary
Severity: Medium
Advisory: GHSA-5wg8-7c9q-794v
CVE: CVE-2020-35912
CWE: CWE-362
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-5wg8-7c9q-794v
Type: github-advisory

## Affected
- crates.io: `lock_api` — affected >=0 <0.4.2

## Details
An issue was discovered in the lock_api crate before 0.4.2 for Rust. A data race can occur because of MappedRwLockWriteGuard unsoundness.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-35912
- https://github.com/Amanieu/parking_lot/pull/262
- https://github.com/Amanieu/parking_lot
- https://rustsec.org/advisories/RUSTSEC-2020-0070.html
