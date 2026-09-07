# [H] Apache Airflow information disclosure vulnerability

## Summary
Severity: High
Advisory: GHSA-xvw9-3mhm-xjqq
CVE: CVE-2022-46651
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-07-12
Source: https://github.com/advisories/GHSA-xvw9-3mhm-xjqq
Type: github-advisory

## Affected
- PyPI: `apache-airflow` — affected >=0 <2.6.3

## Details
Apache Airflow, versions before 2.6.3, is affected by a vulnerability that allows an unauthorized actor to gain access to sensitive information in Connection edit view. This vulnerability is considered low since it requires someone with access to Connection resources specifically updating the connection to exploit it. Users should upgrade to version 2.6.3 or later which has removed the vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-46651
- https://github.com/apache/airflow/pull/32309
- https://github.com/apache/airflow/commit/d01248382fe45a5f5a7fdeed4082a80c5f814ad8
- https://github.com/apache/airflow
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-airflow/PYSEC-2023-103.yaml
- https://lists.apache.org/thread/n45h3y82og125rnlgt6rbm9szfb6q24d
