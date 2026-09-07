# [M] Apache Airflow vulnerable to Exposure of Resource to Wrong Sphere

## Summary
Severity: Medium
Advisory: GHSA-8f57-wcmg-4jmh
CVE: CVE-2023-48291
CWE: CWE-668
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2023-12-21
Source: https://github.com/advisories/GHSA-8f57-wcmg-4jmh
Type: github-advisory

## Affected
- PyPI: `apache-airflow` — affected >=0 <2.8.0

## Details
Apache Airflow, in versions prior to 2.8.0, contains a security vulnerability that allows an authenticated user with limited access to some DAGs, to craft a request that could give the user write access to various DAG resources for DAGs that the user had no access to, thus, enabling the user to clear DAGs they shouldn't.

This is a missing fix for CVE-2023-42792 in Apache Airflow 2.7.2 

Users of Apache Airflow are strongly advised to upgrade to version 2.8.0 or newer to mitigate the risk associated with this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-48291
- https://github.com/apache/airflow/pull/34366
- https://github.com/apache/airflow/commit/4f1b500c47813c54349b7d3e48df0a444fb4826c
- https://github.com/apache/airflow
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-airflow/PYSEC-2023-265.yaml
- https://lists.apache.org/thread/3nl0h014274yjlt1hd02z0q78ftyz0z3
- http://www.openwall.com/lists/oss-security/2023/12/21/1
