# [M] use-after-free vulnerability in Rust array-queue

## Summary
Severity: Medium
Advisory: GHSA-75cq-g75g-rxff
CVE: CVE-2020-35900
CWE: CWE-416
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-75cq-g75g-rxff
Type: github-advisory

## Affected
- crates.io: `array-queue` — affected >=0.3.0

## Details
An issue was discovered in the array-queue crate through 2020-09-26 for Rust. A pop_back() call may lead to a use-after-free.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-35900
- https://github.com/raviqqe/array-queue/issues/2
- https://github.com/raviqqe/array-queue
- https://rustsec.org/advisories/RUSTSEC-2020-0047.html
