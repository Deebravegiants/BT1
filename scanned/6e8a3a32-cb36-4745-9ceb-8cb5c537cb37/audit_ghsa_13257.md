# [M] Apache Superset Server Side Request Forgery vulnerability

## Summary
Severity: Medium
Advisory: GHSA-4fg9-5w46-xmrj
CVE: CVE-2023-36388
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-09-06
Source: https://github.com/advisories/GHSA-4fg9-5w46-xmrj
Type: github-advisory

## Affected
- PyPI: `apache-superset` — affected >=0

## Details
Improper REST API permission in Apache Superset up to and including 2.1.0 allows for an authenticated Gamma users to test network connections, possible SSRF.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-36388
- https://github.com/apache/superset
- https://lists.apache.org/thread/ccmjjz4jp17yc2kcd18qshmdtf7qorfs
