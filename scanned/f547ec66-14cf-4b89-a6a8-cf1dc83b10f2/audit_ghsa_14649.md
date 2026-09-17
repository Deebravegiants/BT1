# [M] python-sql SQL injection vulnerability

## Summary
Severity: Medium
Advisory: GHSA-pq9p-pc3p-9hm4
CVE: CVE-2024-9774
CWE: CWE-150
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-12-27
Source: https://github.com/advisories/GHSA-pq9p-pc3p-9hm4
Type: github-advisory

## Affected
- PyPI: `python-sql` — affected >=0 <1.5.2

## Details
A vulnerability was found in python-sql where unary operators do not escape non-Expression (like `And` and `Or`) which makes any system exposing those vulnerable to an SQL injection attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-9774
- https://access.redhat.com/security/cve/CVE-2024-9774
- https://bugs.tryton.org/python-sql/93
- https://bugzilla.redhat.com/show_bug.cgi?id=2332734
- https://discuss.tryton.org/t/security-release-for-issue-93/7889
- https://discuss.tryton.org/t/security-release-for-issue-93/7889/3
- https://foss.heptapod.net/tryton/python-sql/-/commit/f20551bbb8b3b4c4dd0a2c3d36f377bff6f2f349
- https://github.com/tryton/python-sql
- https://lists.debian.org/debian-lts-announce/2024/10/msg00023.html
