# [H] Uncontrolled Resource Consumption in parse_duration

## Summary
Severity: High
Advisory: GHSA-qpgv-g792-wh6x
CVE: CVE-2021-29932
CWE: CWE-400
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-qpgv-g792-wh6x
Type: github-advisory

## Affected
- crates.io: `parse_duration` — affected >=0

## Details
An issue was discovered in the parse_duration crate through 2021-03-18 for Rust. It allows attackers to cause a denial of service (CPU and memory consumption) via a duration string with a large exponent.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-29932
- https://github.com/zeta12ti/parse_duration/issues/21
- https://github.com/zeta12ti/parse_duration
- https://rustsec.org/advisories/RUSTSEC-2021-0041.html
