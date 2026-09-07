# [M] Data races in lock_api

## Summary
Severity: Medium
Advisory: GHSA-ppj3-7jw3-8vc4
CVE: CVE-2020-35910
CWE: CWE-362
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-ppj3-7jw3-8vc4
Type: github-advisory

## Affected
- crates.io: `lock_api` — affected >=0 <0.4.2

## Details
An issue was discovered in the lock_api crate before 0.4.2 for Rust. A data race can occur because of MappedMutexGuard unsoundness.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-35910
- https://github.com/Amanieu/parking_lot/pull/262
- https://github.com/Amanieu/parking_lot/commit/7de94f95f519d8281cb48457964065b463d26736
- https://github.com/Amanieu/parking_lot
- https://rustsec.org/advisories/RUSTSEC-2020-0070.html
