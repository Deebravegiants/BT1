# [M] Apache Superset: Improper error handling on alerts

## Summary
Severity: Medium
Advisory: GHSA-h7r6-8qmm-hj5r
CVE: CVE-2024-27315
CWE: CWE-200, CWE-209
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-02-28
Source: https://github.com/advisories/GHSA-h7r6-8qmm-hj5r
Type: github-advisory

## Affected
- PyPI: `apache-superset` — affected >=0 <3.0.4
- PyPI: `apache-superset` — affected >=3.1.0 <3.1.1

## Details
An authenticated user with privileges to create Alerts on Alerts & Reports has the capability to generate a specially crafted SQL statement that triggers an error on the database. This error is not properly handled by Apache Superset and may inadvertently surface in the error log of the Alert exposing possibly sensitive data.

This issue affects Apache Superset: before 3.0.4, from 3.1.0 before 3.1.1.

Users are recommended to upgrade to version 3.1.1 or 3.0.4, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-27315
- https://github.com/apache/superset
- https://lists.apache.org/thread/qcwbx7q2s3ynsd405895bx3wcwq32j7z
- http://www.openwall.com/lists/oss-security/2024/02/28/3
