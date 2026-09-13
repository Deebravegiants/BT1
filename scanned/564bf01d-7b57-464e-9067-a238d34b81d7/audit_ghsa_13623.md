# [M] Apache Airflow vulnerable to sensitive information exposure when expose-config is set to non-sensitive-only

## Summary
Severity: Medium
Advisory: GHSA-fpxx-xv4c-gxqp
CVE: CVE-2023-45348
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-10-14
Source: https://github.com/advisories/GHSA-fpxx-xv4c-gxqp
Type: github-advisory

## Affected
- PyPI: `apache-airflow` — affected >=2.7.0 <2.7.2

## Details
Apache Airflow, versions 2.7.0 and 2.7.1, is affected by a vulnerability that allows an authenticated user to retrieve sensitive configuration information when the `expose_config` option is set to `non-sensitive-only`. The `expose_config` option is `False` by default. It is recommended to upgrade to a version that is not affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-45348
- https://github.com/apache/airflow/pull/34712
- https://github.com/apache/airflow/commit/a4a0b5dd3d0ce05311c70bb9a32b66a650dbc0b4
- https://github.com/apache/airflow
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-airflow/PYSEC-2023-204.yaml
- https://lists.apache.org/thread/sy4l5d6tn58hr8r61r2fkt1f0qock9z9
- http://www.openwall.com/lists/oss-security/2023/10/23/2
