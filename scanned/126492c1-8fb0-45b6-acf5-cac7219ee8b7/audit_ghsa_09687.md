# [M] Apache Airflow: JWT token appearing in logs

## Summary
Severity: Medium
Advisory: GHSA-phv5-vq5p-qhp7
CVE: CVE-2026-31987
CWE: CWE-532
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-phv5-vq5p-qhp7
Type: github-advisory

## Affected
- PyPI: `apache-airflow` — affected >=3.0.0 <3.2.0

## Details
JWT Tokens used by tasks were exposed in logs. This could allow UI users to act as Dag Authors. 
Users are advised to upgrade to Airflow version that contains fix.

Users are recommended to upgrade to version 3.2.0, which fixes this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-31987
- https://github.com/apache/airflow/issues/62428
- https://github.com/apache/airflow/issues/62773
- https://github.com/apache/airflow/pull/62964
- https://github.com/apache/airflow
- https://lists.apache.org/thread/pvsrtxzwo9xy6xgknmwslv4zrw70kt6g
- http://www.openwall.com/lists/oss-security/2026/04/16/7
