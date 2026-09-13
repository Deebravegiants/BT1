# [H] Apache Airflow: Wildcard DagVersion Listing Bypasses Per‑DAG RBAC and Leaks Metadata

## Summary
Severity: High
Advisory: GHSA-4m3h-wp5w-5hqh
CVE: CVE-2026-26929
CWE: CWE-732
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-17
Source: https://github.com/advisories/GHSA-4m3h-wp5w-5hqh
Type: github-advisory

## Affected
- PyPI: `apache-airflow` — affected >=3.0.0 <3.1.8

## Details
Apache Airflow versions 3.0.0 through 3.1.7 FastAPI DagVersion listing API does not apply per-DAG authorization filtering when the request is made with dag_id set to "~" (wildcard for all DAGs). As a result, version metadata of DAGs that the requester is not authorized to access is returned.


Users are recommended to upgrade to Apache Airflow 3.1.8 or later, which resolves this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-26929
- https://github.com/apache/airflow/pull/61675
- https://github.com/apache/airflow
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-airflow/PYSEC-2026-14.yaml
- https://lists.apache.org/thread/g5o6khx83jwqvdyn0mlyb0krt35cs9ss
- http://www.openwall.com/lists/oss-security/2026/03/17/4
