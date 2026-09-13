# [H] Apache Airflow vulnerable to Exposure of Sensitive Information to an Unauthorized Actor

## Summary
Severity: High
Advisory: GHSA-r7x6-xfcm-3mxv
CVE: CVE-2023-42781
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-11-12
Source: https://github.com/advisories/GHSA-r7x6-xfcm-3mxv
Type: github-advisory

## Affected
- PyPI: `apache-airflow` — affected >=0 <2.7.3

## Details
Apache Airflow, versions before 2.7.3, has a vulnerability that allows an authorized user who has access to read specific DAGs only, to read information about task instances in other DAGs.  This is a different issue than CVE-2023-42663 but leading to similar outcome.
Users of Apache Airflow are advised to upgrade to version 2.7.3 or newer to mitigate the risk associated with this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-42781
- https://github.com/apache/airflow/pull/34939
- https://github.com/apache/airflow/commit/33ec72948f74f56f2adb5e2d388e60e88e8a3fa3
- https://github.com/apache/airflow
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-airflow/PYSEC-2023-231.yaml
- https://lists.apache.org/thread/7dnl8nszdxqyns57f3dw0sloy5dfl9o1
- http://www.openwall.com/lists/oss-security/2023/11/12/2
