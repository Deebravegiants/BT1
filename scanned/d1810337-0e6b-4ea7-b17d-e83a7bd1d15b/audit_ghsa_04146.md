# [M] Apache Airflow has a Link Following issue

## Summary
Severity: Medium
Advisory: GHSA-89cj-xrpx-j79m
CVE: CVE-2026-40861
CWE: CWE-59
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-01
Source: https://github.com/advisories/GHSA-89cj-xrpx-j79m
Type: github-advisory

## Affected
- PyPI: `apache-airflow` — affected >=0 <3.2.2

## Details
A Dag author could either (a) create a symlink under their task's log directory pointing to an arbitrary file readable by the API server process (read-path attack — e.g. `/etc/passwd` or `airflow.cfg`) or (b) supply a `task_id` containing `..` sequences accepted by the Task SDK's `KEY_REGEX` (write-path attack), and in both cases the FileTaskHandler resolves the log path outside the configured `base_log_folder`, leaking or overwriting arbitrary files. Only affects deployments where the worker log folder is shared with the API server. Users are advised to upgrade to `apache-airflow` 3.2.2 or later. As a defense-in-depth mitigation, deploy the worker and API server with separate log volumes so that worker-controlled paths cannot reach the API server's filesystem.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-40861
- https://github.com/apache/airflow/pull/65325
- https://github.com/apache/airflow
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-airflow/PYSEC-2026-181.yaml
- https://lists.apache.org/thread/823334db2559xjlwt59gpzjz47thnscl
- http://www.openwall.com/lists/oss-security/2026/05/31/1
