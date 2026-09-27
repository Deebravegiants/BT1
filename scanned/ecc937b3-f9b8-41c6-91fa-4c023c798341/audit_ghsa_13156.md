# [M] Apache Superset has improper default REST API permission for Gamma users

## Summary
Severity: Medium
Advisory: GHSA-9832-mgg4-3gr6
CVE: CVE-2023-36387
CWE: CWE-281, CWE-863, CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:L (CVSS_V3)
Published: 2023-09-06
Source: https://github.com/advisories/GHSA-9832-mgg4-3gr6
Type: github-advisory

## Affected
- PyPI: `apache-superset` — affected >=0

## Details
An improper default REST API permission for Gamma users in Apache Superset up to and including 2.1.0 allows for an authenticated Gamma user to test database connections.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-36387
- https://github.com/apache/superset/pull/24185
- https://github.com/apache/superset
- https://lists.apache.org/thread/tt6s6hm8nv6s11z8bfsk3r3d9ov0ogw3
