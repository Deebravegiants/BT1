# [M] Apache Airflow allows authenticated and DAG-view authorized users to modify some DAG run detail values when submitting notes

## Summary
Severity: Medium
Advisory: GHSA-hm9r-7f84-25c9
CVE: CVE-2023-47037
CWE: CWE-285, CWE-863
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2023-11-12
Source: https://github.com/advisories/GHSA-hm9r-7f84-25c9
Type: github-advisory

## Affected
- PyPI: `apache-airflow` — affected >=0 <2.7.3

## Details
Apache Airflow, versions before 2.7.3, is affected by a vulnerability that allows authenticated and DAG-view authorized Users to modify some DAG run detail values when submitting notes. This could have them alter details such as configuration parameters, start date, etc.  Users should upgrade to version 2.7.3 or later which has removed the vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-47037
- https://github.com/apache/airflow/pull/33413
- https://github.com/apache/airflow/commit/2a0106e4edf67c5905ebfcb82a6008662ae0f7ad
- https://github.com/apache/airflow/commit/b7a46c970d638028a4a7643ad000dcee951fb9ef
- https://github.com/apache/airflow
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-airflow/PYSEC-2023-232.yaml
- https://lists.apache.org/thread/04y4vrw1t2xl030gswtctc4nt1w90cb0
- http://www.openwall.com/lists/oss-security/2023/11/12/1
