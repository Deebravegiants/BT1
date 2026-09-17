# [M] Apache Airflow's asset dependency graph did not restrict nodes by the viewer's DAG read permissions

## Summary
Severity: Medium
Advisory: GHSA-w7rc-q6cm-f5gm
CVE: CVE-2026-40690
CWE: CWE-1220
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-04-24
Source: https://github.com/advisories/GHSA-w7rc-q6cm-f5gm
Type: github-advisory

## Affected
- PyPI: `apache-airflow` — affected >=0 <3.2.1rc1

## Details
The asset dependency graph did not restrict nodes by the viewer's DAG read permissions: a user with read access to at least one DAG could browse the asset graph for any other asset in the deployment and learn the existence and names of DAGs and assets outside their authorized scope.

Users are recommended to upgrade to version 3.2.1, which fixes this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-40690
- https://github.com/apache/airflow/pull/65273
- https://github.com/apache/airflow/commit/cf3452d76e2ef5a8bae247f9fc90c759ff9df02f
- https://github.com/apache/airflow
- https://lists.apache.org/thread/bqt7y4g2cpj396b0sd20lv510ff19ndl
- http://www.openwall.com/lists/oss-security/2026/04/24/4
