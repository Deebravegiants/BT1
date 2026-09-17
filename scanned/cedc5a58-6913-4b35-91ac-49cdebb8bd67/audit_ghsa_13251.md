# [M] Apache Airflow Incorrect Authorization vulnerability

## Summary
Severity: Medium
Advisory: GHSA-wpg8-mf6h-gm92
CVE: CVE-2023-40611
CWE: CWE-863
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2023-09-12
Source: https://github.com/advisories/GHSA-wpg8-mf6h-gm92
Type: github-advisory

## Affected
- PyPI: `apache-airflow` — affected >=0 <2.7.1

## Details
Apache Airflow, versions before 2.7.1, is affected by a vulnerability that allows authenticated and DAG-view authorized Users to modify some DAG run detail values when submitting notes. This could have them alter details such as configuration parameters, start date, etc.

Users should upgrade to version 2.7.1 or later which has removed the vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-40611
- https://github.com/apache/airflow/pull/33413
- https://github.com/apache/airflow/commit/2a0106e4edf67c5905ebfcb82a6008662ae0f7ad
- https://github.com/apache/airflow/commit/b7a46c970d638028a4a7643ad000dcee951fb9ef
- https://github.com/apache/airflow
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-airflow/PYSEC-2023-170.yaml
- https://lists.apache.org/thread/8y9xk1s3j4qr36yzqn8ogbn9fl7pxrn0
- http://www.openwall.com/lists/oss-security/2023/11/12/1
