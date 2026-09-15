# [H] Remote code execution (RCE) in Apache Airflow

## Summary
Severity: High
Advisory: GHSA-rvmq-4x66-q7j3
CVE: CVE-2020-11978
CWE: CWE-77, CWE-78
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H/E:H (CVSS_V3)
Published: 2020-07-27
Source: https://github.com/advisories/GHSA-rvmq-4x66-q7j3
Type: github-advisory

## Affected
- PyPI: `apache-airflow` — affected >=0 <1.10.11rc1

## Details
An issue was found in Apache Airflow versions 1.10.10 and below. A remote code/command injection vulnerability was discovered in one of the example DAGs shipped with Airflow which would allow any authenticated user to run arbitrary commands as the user running airflow worker/scheduler (depending on the executor in use). If you already have examples disabled by setting `load_examples=False` in the config then you are not vulnerable.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-11978
- https://github.com/apache/airflow/pull/9143
- https://github.com/apache/airflow/commit/2fa51576e1283f5732e38fada686fd248d9c3a1e
- https://github.com/apache/airflow/commit/4d8599e8b0520ff4226fbad72f724afae50fdd08
- https://github.com/apache/airflow
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-airflow/PYSEC-2020-14.yaml
- https://lists.apache.org/thread.html/r7255cf0be3566f23a768e2a04b40fb09e52fcd1872695428ba9afe91%40%3Cusers.airflow.apache.org%3E
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2020-11978
- http://packetstormsecurity.com/files/162908/Apache-Airflow-1.10.10-Remote-Code-Execution.html
- http://packetstormsecurity.com/files/174764/Apache-Airflow-1.10.10-Remote-Code-Execution.html
