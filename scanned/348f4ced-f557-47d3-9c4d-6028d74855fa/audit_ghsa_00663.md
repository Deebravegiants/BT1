# [M] SSRF vulnerability in Apache Airflow

## Summary
Severity: Medium
Advisory: GHSA-6r3p-fcvm-xh7c
CVE: CVE-2020-17513
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2020-12-17
Source: https://github.com/advisories/GHSA-6r3p-fcvm-xh7c
Type: github-advisory

## Affected
- PyPI: `apache-airflow` — affected >=0 <1.10.13

## Details
In Apache Airflow versions prior to 1.10.13, the Charts and Query View of the old (Flask-admin based) UI were vulnerable for SSRF attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-17513
- https://github.com/apache/airflow/commit/b606b871226d649913a37fd074eeae5d86ebc3a1
- https://github.com/advisories/GHSA-6r3p-fcvm-xh7c
- https://github.com/apache/airflow
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-airflow/PYSEC-2020-20.yaml
- https://lists.apache.org/thread.html/rb3647269f07cc2775ca6568cbfd4994d862c842a58120d2aba9c658a%40%3Cusers.airflow.apache.org%3E
