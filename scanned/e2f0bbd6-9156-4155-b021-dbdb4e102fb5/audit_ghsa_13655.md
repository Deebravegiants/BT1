# [M] Apache Airflow vulnerable to sensitive information exposure when users list warnings for all DAGs

## Summary
Severity: Medium
Advisory: GHSA-cgx2-rrmr-jx43
CVE: CVE-2023-42780
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-10-14
Source: https://github.com/advisories/GHSA-cgx2-rrmr-jx43
Type: github-advisory

## Affected
- PyPI: `apache-airflow` — affected >=0 <2.7.2

## Details
Apache Airflow, versions prior to 2.7.2, contains a security vulnerability that allows authenticated users of Airflow to list warnings for all DAGs, even if the user had no permission to see those DAGs. It would reveal the dag_ids and the stack-traces of import errors for those DAGs with import errors. Users of Apache Airflow are advised to upgrade to version 2.7.2 or newer to mitigate the risk associated with this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-42780
- https://github.com/apache/airflow/pull/34355
- https://github.com/apache/airflow/commit/cf4eb3fb9b5cf4a8369b890e39523d4c05eed161
- https://github.com/apache/airflow
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-airflow/PYSEC-2023-202.yaml
- https://lists.apache.org/thread/h5tvsvov8j55wojt5sojdprs05oby34d
