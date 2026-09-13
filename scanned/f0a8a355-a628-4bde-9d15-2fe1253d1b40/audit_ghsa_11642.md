# [M] Apache Airflow Provider for Databricks: TLS Certificate Verification is Disabled in Databricks Provider K8s Token Exchange

## Summary
Severity: Medium
Advisory: GHSA-wrpj-755p-x363
CVE: CVE-2026-32794
CWE: CWE-295
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-03-31
Source: https://github.com/advisories/GHSA-wrpj-755p-x363
Type: github-advisory

## Affected
- PyPI: `apache-airflow` — affected >=1.10.0 <1.12.0

## Details
Improper Certificate Validation vulnerability in Apache Airflow Provider for Databricks. Provider code did not validate certificates for connections to Databricks back-end which could result in a man-of-a-middle attack that traffic is intercepted and manipulated or credentials exfiltrated w/o notice.

This issue affects Apache Airflow Provider for Databricks: from 1.10.0 before 1.12.0.

Users are recommended to upgrade to version 1.12.0, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-32794
- https://github.com/apache/airflow/pull/63704
- https://github.com/apache/airflow
- https://lists.apache.org/thread/hn17yqsgsdtl81llvhf80rkp53hnz5nb
- http://www.openwall.com/lists/oss-security/2026/03/30/9
