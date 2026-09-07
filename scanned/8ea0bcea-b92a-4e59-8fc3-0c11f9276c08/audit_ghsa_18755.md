# [M] Apache Airflow has a command injection vulnerability in "example_dag_decorator"

## Summary
Severity: Medium
Advisory: GHSA-v3c9-j6h9-66v4
CVE: CVE-2025-54941
CWE: CWE-78
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2025-10-30
Source: https://github.com/advisories/GHSA-v3c9-j6h9-66v4
Type: github-advisory

## Affected
- PyPI: `apache-airflow` — affected >=3.0.0 <3.0.5

## Details
An example dag `example_dag_decorator` had non-validated parameter that allowed the UI user to redirect the example to a malicious server and execute code on worker. This however required that the example dags are enabled in production (not default) or the example dag code copied to build your own similar dag. If you used the `example_dag_decorator` please review it and apply the changes implemented in Airflow 3.0.5 accordingly.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-54941
- https://github.com/apache/airflow
- https://lists.apache.org/thread/c6q6nofc6xl5bms039ks9b34v0v36df1
- http://www.openwall.com/lists/oss-security/2025/10/29/6
