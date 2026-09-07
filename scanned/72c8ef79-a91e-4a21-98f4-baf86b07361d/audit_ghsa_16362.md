# [M] Apache Superset: Improper validation of SQL statements allows for unauthorized access to data

## Summary
Severity: Medium
Advisory: GHSA-5474-f7g5-273q
CVE: CVE-2024-24773
CWE: CWE-863
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-02-28
Source: https://github.com/advisories/GHSA-5474-f7g5-273q
Type: github-advisory

## Affected
- PyPI: `apache-superset` — affected >=0 <3.0.4
- PyPI: `apache-superset` — affected >=3.1.0 <3.1.1

## Details
Improper parsing of nested SQL statements on SQLLab would allow authenticated users to surpass their data authorization scope.
This issue affects Apache Superset: before 3.0.4, from 3.1.0 before 3.1.1.

Users are recommended to upgrade to version 3.1.1, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-24773
- https://github.com/apache/superset
- https://lists.apache.org/thread/h66fy6nj41cfx07zh7l552w6dmtjh501
- http://www.openwall.com/lists/oss-security/2024/02/28/4
