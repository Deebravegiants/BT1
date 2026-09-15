# [M] Apache Superset Incorrect Authorization vulnerability

## Summary
Severity: Medium
Advisory: GHSA-299q-3p96-5898
CVE: CVE-2024-28148
CWE: CWE-863
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-05-07
Source: https://github.com/advisories/GHSA-299q-3p96-5898
Type: github-advisory

## Affected
- PyPI: `apache-superset` — affected >=0 <3.1.2

## Details
An authenticated user could potentially access metadata for a datasource they are not authorized to view by submitting a targeted REST API request. This issue affects Apache Superset before 3.1.2.

Users are recommended to upgrade to version 3.1.2 or above, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-28148
- https://github.com/apache/superset
- https://lists.apache.org/thread/n27wlbd05oc6bgjh28d5pxzsrrph8dgo
