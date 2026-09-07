# [M] Apache Superset has Improper Access Control

## Summary
Severity: Medium
Advisory: GHSA-8f5j-mgx9-5hm5
CVE: CVE-2022-45438
CWE: CWE-284, CWE-668
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-01-16
Source: https://github.com/advisories/GHSA-8f5j-mgx9-5hm5
Type: github-advisory

## Affected
- PyPI: `apache-superset` — affected >=0
- PyPI: `apache-superset` — affected 2.0.0

## Details
When explicitly enabling the feature flag `DASHBOARD_CACHE` (disabled by default), the system allowed for an unauthenticated user to access dashboard configuration metadata using a REST API Get endpoint. This issue affects Apache Superset version 1.5.2 and prior versions and version 2.0.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-45438
- https://github.com/apache/superset
- https://lists.apache.org/thread/snxbkf2x9kww7s0wkmydct9nhqqn9rv9
