# [M] Apache Airflow: Ignored Airflow Permission

## Summary
Severity: Medium
Advisory: GHSA-h574-6646-vfxx
CVE: CVE-2024-28746
CWE: CWE-281
Ecosystem: PyPI
Published: 2024-03-14
Source: https://github.com/advisories/GHSA-h574-6646-vfxx
Type: github-advisory

## Affected
- PyPI: `apache-airflow` — affected >=2.8.0 <2.8.3rc1

## Details
Apache Airflow, versions 2.8.0 through 2.8.2, has a vulnerability that allows an authenticated user with limited permissions to access resources such as variables, connections, etc from the UI which they do not have permission to access. 

Users of Apache Airflow are recommended to upgrade to version 2.8.3 or newer to mitigate the risk associated with this vulnerability

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-28746
- https://github.com/apache/airflow/pull/37881
- https://github.com/apache/airflow/commit/89e7f3e7bdf2126bbbcd959dc10d65ef92773cca
- https://github.com/apache/airflow
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-airflow/PYSEC-2024-46.yaml
- https://lists.apache.org/thread/b4pffc7w7do6qgk4jjbyxvdz5odrvny7
- http://www.openwall.com/lists/oss-security/2024/03/13/5
