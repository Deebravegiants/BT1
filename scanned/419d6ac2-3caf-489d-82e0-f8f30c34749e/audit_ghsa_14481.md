# [M] Sensitive Information in Error Messages in Apache Airflow

## Summary
Severity: Medium
Advisory: GHSA-h6g5-wqqr-3mw3
CVE: CVE-2023-25695
CWE: CWE-209
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-03-15
Source: https://github.com/advisories/GHSA-h6g5-wqqr-3mw3
Type: github-advisory

## Affected
- PyPI: `apache-airflow` — affected >=0 <2.5.2rc1

## Details
Generation of Error Message Containing Sensitive Information vulnerability in Apache Software Foundation Apache Airflow.This issue affects Apache Airflow: before 2.5.2. The traceback contains information that might be useful for a potential attacker to better target their attack (Python/Airflow version, node name). This information should not be shown if traceback is shown to unauthenticated user.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-25695
- https://github.com/apache/airflow/pull/29501
- https://github.com/apache/airflow/commit/965e76d9ed00ef354a834739ac46f24068630951
- https://github.com/apache/airflow
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-airflow/PYSEC-2023-2.yaml
- https://lists.apache.org/thread/z8w6ckzs61ql365tv4d19k82o67r15p2
