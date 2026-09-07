# [H] Uncontrolled recursion in ammonia

## Summary
Severity: High
Advisory: GHSA-5hp8-35wj-m525
CVE: CVE-2019-15542
CWE: CWE-674
Ecosystem: crates.io
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-5hp8-35wj-m525
Type: github-advisory

## Affected
- crates.io: `ammonia` — affected >=0 <2.1.0

## Details
An issue was discovered in the ammonia crate before 2.1.0 for Rust. There is uncontrolled recursion during HTML DOM tree serialization.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-15542
- https://github.com/rust-ammonia/ammonia
- https://github.com/rust-ammonia/ammonia/blob/master/CHANGELOG.md#210
- https://rustsec.org/advisories/RUSTSEC-2019-0001.html
