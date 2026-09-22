# [C] Use after free in rio

## Summary
Severity: Critical
Advisory: GHSA-8rc5-mr4f-m243
CVE: CVE-2020-35876
CWE: CWE-416, CWE-772
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-8rc5-mr4f-m243
Type: github-advisory

## Affected
- crates.io: `rio` — affected >=0

## Details
An issue was discovered in the rio crate through 2020-05-11 for Rust. A struct can be leaked, allowing attackers to obtain sensitive information, cause a use-after-free, or cause a data race.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-35876
- https://github.com/spacejam/rio/issues/11
- https://github.com/spacejam/rio/pull/31
- https://github.com/spacejam/rio
- https://rustsec.org/advisories/RUSTSEC-2020-0021.html
