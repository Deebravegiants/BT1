# [H] Apache Airflow: Bypass permission verification to read code of other dags

## Summary
Severity: High
Advisory: GHSA-vm5m-qmrx-fw8w
CVE: CVE-2023-50944
CWE: CWE-862
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-01-24
Source: https://github.com/advisories/GHSA-vm5m-qmrx-fw8w
Type: github-advisory

## Affected
- PyPI: `apache-airflow` — affected >=0 <2.8.1rc1

## Details
Apache Airflow, versions before 2.8.1, have a vulnerability that allows an authenticated user to access the source code of a DAG to which they don't have access. This vulnerability is considered low since it requires an authenticated user to exploit it. Users are recommended to upgrade to version 2.8.1, which fixes this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-50944
- https://github.com/apache/airflow/pull/36257
- https://github.com/apache/airflow/commit/8d76538d6e105947272b000581c6fabec20146b1
- https://github.com/apache/airflow
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-airflow/PYSEC-2024-14.yaml
- https://lists.apache.org/thread/92krb5mpcq8qrw4t4j5oooqw7hgd8q7h
- http://www.openwall.com/lists/oss-security/2024/01/24/5
