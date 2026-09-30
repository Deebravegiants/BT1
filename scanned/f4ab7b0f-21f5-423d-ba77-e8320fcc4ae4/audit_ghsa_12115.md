# [H] Apache Airflow Providers Http has Unsafe Pickle Deserializatio leading to RCE via HttpOperator

## Summary
Severity: High
Advisory: GHSA-9r5j-7r2x-rv4g
CVE: CVE-2025-69219
CWE: CWE-913
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-09
Source: https://github.com/advisories/GHSA-9r5j-7r2x-rv4g
Type: github-advisory

## Affected
- PyPI: `apache-airflow-providers-http` — affected >=0 <6.0.0

## Details
A user with access to the DB could craft a database entry that would result in executing code on Triggerer - which gives anyone who have access to DB the same permissions as Dag Author. Since direct DB access is not usual and recommended for Airflow, the likelihood of it making any damage is low.

Users should upgrade to version 6.0.0 of the provider to avoid even that risk.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-69219
- https://github.com/apache/airflow/pull/61662
- https://github.com/apache/airflow/commit/97839f7b0a8ae66d6079bb7fad5a363068f61617
- https://github.com/apache/airflow
- https://lists.apache.org/thread/zjkfb2njklro68tqzym092r4w65m5dq0
- http://www.openwall.com/lists/oss-security/2026/03/09/1
