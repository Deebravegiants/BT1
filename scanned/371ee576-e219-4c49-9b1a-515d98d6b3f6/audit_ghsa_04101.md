# [H] Apache Airflow vulnerable to CSRF Attacks

## Summary
Severity: High
Advisory: GHSA-w6j4-3gh2-9f5j
CVE: CVE-2019-0229
CWE: CWE-352
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-04-18
Source: https://github.com/advisories/GHSA-w6j4-3gh2-9f5j
Type: github-advisory

## Affected
- PyPI: `apache-airflow` — affected >=0 <1.10.3

## Details
A number of HTTP endpoints in the Airflow webserver (both RBAC and classic) did not have adequate protection and were vulnerable to cross-site request forgery attacks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-0229
- https://github.com/advisories/GHSA-w6j4-3gh2-9f5j
- https://github.com/apache/airflow
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-airflow/PYSEC-2019-215.yaml
- https://lists.apache.org/thread.html/2de387213d45bc626d27554a1bde7b8c67d08720901f82a50b6f4231@%3Cdev.airflow.apache.org%3E
- https://web.archive.org/web/20200227081055/http://www.securityfocus.com/bid/107869
- http://www.openwall.com/lists/oss-security/2019/04/10/6
