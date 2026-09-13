# [H] Apache Airflow: RCE by race condition in example_xcom dag

## Summary
Severity: High
Advisory: GHSA-q2hg-643c-gw8h
CVE: CVE-2025-54550
CWE: CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-q2hg-643c-gw8h
Type: github-advisory

## Affected
- PyPI: `apache-airflow` — affected >=0 <3.2.0

## Details
The example example_xcom that was included in airflow documentation implemented unsafe pattern of reading value
from xcom in the way that could be exploited to allow UI user who had access to modify XComs to perform arbitrary
execution of code on the worker. Since the UI users are already highly trusted, this is a Low severity vulnerability.

It does not affect Airflow release - example_dags are not supposed to be enabled in production environment, however
users following the example could replicate the bad pattern. Documentation of Airflow 3.2.0 contains version of
the example with improved resiliance for that case.

Users who followed that pattern are advised to adjust their implementations accordingly.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-54550
- https://github.com/apache/airflow/pull/63200
- https://github.com/apache/airflow
- https://lists.apache.org/thread/3mf4cfx070ofsnf9qy0s2v5gqb5sc2g1
- http://www.openwall.com/lists/oss-security/2026/04/15/1
