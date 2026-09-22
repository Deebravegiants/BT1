# [H] Apache Airflow has DAG Author Code Execution possibility in airflow-scheduler

## Summary
Severity: High
Advisory: GHSA-g5hv-r743-v8pm
CVE: CVE-2024-39877
CWE: CWE-277, CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-07-17
Source: https://github.com/advisories/GHSA-g5hv-r743-v8pm
Type: github-advisory

## Affected
- PyPI: `apache-airflow` — affected >=2.4.0 <2.9.3

## Details
Apache Airflow 2.4.0, and versions before 2.9.3, has a vulnerability that allows authenticated DAG authors to craft a doc_md parameter in a way that could execute arbitrary code in the scheduler context, which should be forbidden according to the Airflow Security model. Users should upgrade to version 2.9.3 or later which has removed the vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-39877
- https://github.com/apache/airflow/pull/40522
- https://github.com/apache/airflow/commit/8159f6e24704f5e0e3b3217cf79ecf5083dce531
- https://github.com/apache/airflow
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-airflow/PYSEC-2024-190.yaml
- https://lists.apache.org/thread/1xhj9dkp37d6pzn24ll2mf94wbqnb2y1
- http://www.openwall.com/lists/oss-security/2024/07/16/7
