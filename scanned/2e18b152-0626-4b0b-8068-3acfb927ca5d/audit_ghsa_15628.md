# [M] Apache Airflow Potential Cross-site Scripting Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-j482-47xf-p25c
CVE: CVE-2024-39863
CWE: CWE-74, CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-07-17
Source: https://github.com/advisories/GHSA-j482-47xf-p25c
Type: github-advisory

## Affected
- PyPI: `apache-airflow` — affected >=0 <2.9.3

## Details
Apache Airflow versions before 2.9.3 have a vulnerability that allows an authenticated attacker to inject a malicious link when installing a provider. Users are recommended to upgrade to version 2.9.3, which fixes this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-39863
- https://github.com/apache/airflow/pull/40475
- https://github.com/apache/airflow/commit/f18f48492dc69f392e45567580b6ddb0c070ea58
- https://github.com/apache/airflow
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-airflow/PYSEC-2024-189.yaml
- https://lists.apache.org/thread/gxkvs279f1mbvckv5q65worr6how20o3
- http://www.openwall.com/lists/oss-security/2024/07/16/6
