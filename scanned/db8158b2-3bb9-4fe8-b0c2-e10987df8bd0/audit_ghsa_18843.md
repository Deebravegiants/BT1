# [H] pg8000 SQL injection vulnerability via a specially crafted Python list input

## Summary
Severity: High
Advisory: GHSA-wq2g-r956-j8cc
CVE: CVE-2025-61385
CWE: CWE-89
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2025-10-27
Source: https://github.com/advisories/GHSA-wq2g-r956-j8cc
Type: github-advisory

## Affected
- PyPI: `pg8000` — affected >=0 <1.31.5

## Details
SQL injection vulnerability in tlocke pg8000 1.31.4 allows remote attackers to execute arbitrary SQL commands via a specially crafted Python list input to function pg8000.native.literal.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-61385
- https://codeberg.org/tlocke/pg8000
- https://codeberg.org/tlocke/pg8000/commit/8663c746b02286c32f19c385f0e2e5da9e4fa140
- https://github.com/bmcyver/vulnerability-research/tree/main/CVE-2025-61385
