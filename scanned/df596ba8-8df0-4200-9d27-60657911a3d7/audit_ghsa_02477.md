# [M] Data race in disrustor

## Summary
Severity: Medium
Advisory: GHSA-w9r2-qrpm-4rmj
CVE: CVE-2020-36470
CWE: CWE-362
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-w9r2-qrpm-4rmj
Type: github-advisory

## Affected
- crates.io: `disrustor` — affected >=0 <0.3.0

## Details
An issue was discovered in the disrustor crate through 2020-12-17 for Rust. RingBuffer doe not properly limit the number of mutable references.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36470
- https://github.com/sklose/disrustor/issues/1
- https://github.com/sklose/disrustor/commit/0be7aed40adbac51a50a3b95c815349a40d79ca6
- https://github.com/sklose/disrustor
- https://rustsec.org/advisories/RUSTSEC-2020-0150.html
