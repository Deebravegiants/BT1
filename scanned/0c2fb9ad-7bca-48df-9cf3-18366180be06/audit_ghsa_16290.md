# [M] Apache Superset: Improper authorization validation on dashboards and charts import

## Summary
Severity: Medium
Advisory: GHSA-3v9r-885j-762g
CVE: CVE-2024-26016
CWE: CWE-863
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-02-28
Source: https://github.com/advisories/GHSA-3v9r-885j-762g
Type: github-advisory

## Affected
- PyPI: `apache-superset` — affected >=0 <3.0.4
- PyPI: `apache-superset` — affected >=3.1.0 <3.1.1

## Details
A low privilege authenticated user could import an existing dashboard or chart that they do not have access to and then modify its metadata, thereby gaining ownership of the object. However, it's important to note that access to the analytical data of these charts and dashboards would still be subject to validation based on data access privileges.

This issue affects Apache Superset: before 3.0.4, from 3.1.0 before 3.1.1.Users are recommended to upgrade to version 3.1.1, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-26016
- https://github.com/apache/superset
- https://lists.apache.org/thread/76v1jjcylgk4p3m0258qr359ook3vl8s
- http://www.openwall.com/lists/oss-security/2024/02/28/7
