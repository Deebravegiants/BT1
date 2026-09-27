# [M] Apache Superset: Improper Neutralization of custom SQL on embedded context

## Summary
Severity: Medium
Advisory: GHSA-m6jm-3v38-76j4
CVE: CVE-2024-24772
CWE: CWE-20, CWE-89
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-02-28
Source: https://github.com/advisories/GHSA-m6jm-3v38-76j4
Type: github-advisory

## Affected
- PyPI: `apache-superset` — affected >=0 <3.0.4
- PyPI: `apache-superset` — affected >=3.1.0 <3.1.1

## Details
A guest user could exploit a chart data REST API and send arbitrary SQL statements that on error could leak information from the underlying analytics database.This issue affects Apache Superset: before 3.0.4, from 3.1.0 before 3.1.1.

Users are recommended to upgrade to version 3.1.1 or 3.0.4, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-24772
- https://github.com/apache/superset
- https://lists.apache.org/thread/gfl3ckwy6y9tpz9jmpv62orh2q346sn5
- http://www.openwall.com/lists/oss-security/2024/02/28/5
