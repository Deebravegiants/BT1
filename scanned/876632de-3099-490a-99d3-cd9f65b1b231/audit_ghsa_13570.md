# [M] Apache Airflow vulnerable to privilege escalation

## Summary
Severity: Medium
Advisory: GHSA-j3w8-2p2h-mrr9
CVE: CVE-2023-42792
CWE: CWE-668
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2023-10-14
Source: https://github.com/advisories/GHSA-j3w8-2p2h-mrr9
Type: github-advisory

## Affected
- PyPI: `apache-airflow` — affected >=0 <2.7.2

## Details
Apache Airflow, in versions prior to 2.7.2, contains a security vulnerability that allows an authenticated user with limited access to some DAGs, to craft a request that could give the user write access to various DAG resources for DAGs that the user had no access to, thus, enabling the user to clear DAGs they shouldn't.

Users of Apache Airflow are strongly advised to upgrade to version 2.7.2 or newer to mitigate the risk associated with this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-42792
- https://github.com/apache/airflow/pull/34366
- https://github.com/apache/airflow
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-airflow/PYSEC-2023-203.yaml
- https://lists.apache.org/thread/1spbo9nkn49fc2hnxqm9tf6mgqwp9tjq
- http://www.openwall.com/lists/oss-security/2023/12/21/1
