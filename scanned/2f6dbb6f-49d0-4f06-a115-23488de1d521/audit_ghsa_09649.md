# [M] Apache Airflow has an authorization bypass in DagRun wait endpoint

## Summary
Severity: Medium
Advisory: GHSA-r7vr-m4jw-r794
CVE: CVE-2026-34538
CWE: CWE-668
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-09
Source: https://github.com/advisories/GHSA-r7vr-m4jw-r794
Type: github-advisory

## Affected
- PyPI: `apache-airflow` — affected >=3.0.0 <3.2.0

## Details
Apache Airflow versions 3.0.0 through 3.1.8 DagRun wait endpoint returns XCom result values even to users who only have DAG Run read permissions, such as the Viewer role.This behavior conflicts with the FAB RBAC model, which treats XCom as a separate protected resource, and with the security model documentation that defines the Viewer role as read-only.

Airflow uses the FAB Auth Manager to manage access control on a per-resource basis. The Viewer role is intended to be read-only by default, and the security model documentation defines Viewer users as those who can inspect DAGs without accessing sensitive execution results.

Users are recommended to upgrade to Apache Airflow 3.2.0 which resolves this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-34538
- https://github.com/apache/airflow/pull/64415
- https://github.com/apache/airflow
- https://github.com/apache/airflow/releases/tag/3.2.0
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-airflow/PYSEC-2026-21.yaml
- https://lists.apache.org/thread/9mq3msqhmgjwdzbr6bgthj4brb3oz9fl
- http://www.openwall.com/lists/oss-security/2026/04/09/9
