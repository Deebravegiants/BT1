# [M] Apache Airflow error reporting may expose full kwargs

## Summary
Severity: Medium
Advisory: GHSA-gfw7-2v73-69wg
CVE: CVE-2025-65995
CWE: CWE-209
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-02-21
Source: https://github.com/advisories/GHSA-gfw7-2v73-69wg
Type: github-advisory

## Affected
- PyPI: `apache-airflow` — affected >=0 <2.11.1
- PyPI: `apache-airflow` — affected >=3.0.0b1 <3.1.5rc1

## Details
When a DAG failed during parsing, Airflow’s error-reporting in the UI could include the full kwargs passed to the operators. If those kwargs contained sensitive values (such as secrets), they might be exposed in the UI tracebacks to authenticated users who had permission to view that DAG. 

The issue has been fixed in Airflow 3.1.5rc1 and 2.11.1, and users are strongly advised to upgrade to prevent potential disclosure of sensitive information.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-65995
- https://github.com/apache/airflow/pull/58252
- https://github.com/apache/airflow/pull/61883
- https://github.com/apache/airflow
- https://lists.apache.org/thread/1qzlrjo2wmlzs0rrgzgslj2pzkor0dr2
- http://www.openwall.com/lists/oss-security/2025/12/12/2
