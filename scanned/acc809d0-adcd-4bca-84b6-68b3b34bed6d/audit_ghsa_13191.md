# [H] Apache Airflow information exposure vulnerability

## Summary
Severity: High
Advisory: GHSA-mjqh-v5f2-g2mw
CVE: CVE-2023-40712
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-09-12
Source: https://github.com/advisories/GHSA-mjqh-v5f2-g2mw
Type: github-advisory

## Affected
- PyPI: `apache-airflow` — affected >=0 <2.7.1

## Details
Apache Airflow, versions before 2.7.1, is affected by a vulnerability that allows authenticated users who have access to see the task/dag in the UI, to craft a URL, which could lead to unmasking the secret configuration of the task that otherwise would be masked in the UI.

Users are strongly advised to upgrade to version 2.7.1 or later which has removed the vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-40712
- https://github.com/apache/airflow/pull/33512
- https://github.com/apache/airflow/pull/33516
- https://github.com/apache/airflow/commit/4390524a41fdfd2d57f1d2dc98ad7b4009c8399e
- https://github.com/apache/airflow/commit/d9814eb3a2fc1dbbb885a0a2c1b7a23ce1cfa148
- https://github.com/apache/airflow
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-airflow/PYSEC-2023-171.yaml
- https://lists.apache.org/thread/jw1yv4lt6hpowqbb0x4o3tdp0jhx2bts
