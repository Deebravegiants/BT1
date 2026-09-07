# [H] Apache Airflow Path Traversal vulnerability

## Summary
Severity: High
Advisory: GHSA-ggwr-4vr8-g7wv
CVE: CVE-2023-22887
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-07-12
Source: https://github.com/advisories/GHSA-ggwr-4vr8-g7wv
Type: github-advisory

## Affected
- PyPI: `apache-airflow` — affected >=0 <2.6.3

## Details
Apache Airflow, versions before 2.6.3, is affected by a vulnerability that allows an attacker to perform unauthorized file access outside the intended directory structure by manipulating the run_id parameter. This vulnerability is considered low since it requires an authenticated user to exploit it. It is recommended to upgrade to a version that is not affected

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-22887
- https://github.com/apache/airflow/pull/32293
- https://github.com/apache/airflow/commit/05bd90f563649f2e9c8f0c85cf5838315a665a02
- https://github.com/apache/airflow/commit/8ff7dfbd9e76aa40b04adeb231df3820606f5ba3
- https://github.com/apache/airflow
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-airflow/PYSEC-2023-104.yaml
- https://lists.apache.org/thread/rxddqs76r6rkxsg1n24d029zys67qwwo
